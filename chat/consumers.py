import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
User = get_user_model()
from django.utils import timezone
from .models import Message


def room_name_for(u1, u2):
    return f"dm_{'_'.join(sorted([u1, u2]))}"


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        self.me = self.scope["user"].username
        self.other = self.scope["url_route"]["kwargs"]["username"]
        self.room_name = room_name_for(self.me, self.other)

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
        print(f"✅ {self.me} connected to room {self.room_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
        print(f"❌ {self.me} disconnected from room {self.room_name}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            kind = data.get("type")
        except Exception as e:
            print("❗ Error parsing incoming JSON:", e)
            return

        # 👀 Typing event
        if kind == "typing":
            await self.channel_layer.group_send(self.room_name, {
                "type": "typing.event",
                "user": self.me,
            })
            return

        # 💬 Sending message
        if kind == "message":
            content = data.get("content", "").strip()
            if not content:
                return

            try:
                other_user = await User.objects.aget(username=self.other)
                msg = await Message.objects.acreate(
                    sender=self.scope["user"],
                    receiver=other_user,
                    content=content
                )

                payload = {
                    "type": "chat.event",
                    "event": "message",
                    "message": {
                        "id": msg.id,
                        "sender": self.me,
                        "receiver": self.other,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat(),
                    },
                }

                await self.channel_layer.group_send(self.room_name, payload)
                print(f"📤 Sent message from {self.me} to {self.other}: {msg.content}")

            except Exception as e:
                print("❗ Error sending message:", str(e))
            return

        # ✅ Mark message as read
        if kind == "read":
            msg_id = data.get("id")
            try:
                msg = await Message.objects.aget(id=msg_id, receiver=self.scope["user"])
                msg.read_at = timezone.now()
                await msg.asave(update_fields=["read_at"])

                await self.channel_layer.group_send(self.room_name, {
                    "type": "chat.event",
                    "event": "read",
                    "id": msg.id,
                    "read_at": msg.read_at.isoformat(),
                })
                print(f"✅ Message {msg.id} marked as read by {self.me}")

            except Message.DoesNotExist:
                print(f"❗ Message {msg_id} does not exist or unauthorized read attempt")

    # 🔄 Receive chat events from group
    async def chat_event(self, event):
        await self.send(text_data=json.dumps(event))