from rest_framework.viewsets import ModelViewSet
from django.db.models import Q, Max, Count
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Message, Reaction
from .serializers import MessageSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework import generics, permissions, status
from django.utils import timezone
from rest_framework.parsers import MultiPartParser
import json
from django.contrib.auth import get_user_model
User = get_user_model()


class MessageViewSet(ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class ReceivedMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # current logged in user
        messages = Message.objects.filter(receiver=user)  # messages sent to this user
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

class SentMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, username):
        try:
            receiver = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'detail': 'Receiver not found'}, status=404)

        message = request.data.get("message")
        if not message:
            return Response({'message': 'Message content is required'}, status=400)

        msg = Message.objects.create(sender=request.user, receiver=receiver, content=message)
        serializer = MessageSerializer(msg)
        return Response(serializer.data, status=201)

#recations 



class AddReactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, message_id):
        emoji = request.data.get("emoji")
        reaction = Reaction.objects.create(
            message_id=message_id,
            user=request.user,
            emoji=emoji
        )
        return Response({"message": "Reaction added."})
# edit message 


class EditMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        msg = get_object_or_404(Message, pk=pk)
        # Only the sender can edit
        if msg.sender != request.user:
            return Response({"detail": "Not allowed"}, status=status.HTTP_403_FORBIDDEN)

        content = request.data.get("content", "").strip()
        if not content:
            return Response({"content": ["This field may not be blank."]},
                            status=status.HTTP_400_BAD_REQUEST)

        if msg.is_deleted:
            return Response({"detail": "Cannot edit a deleted message."},
                            status=status.HTTP_400_BAD_REQUEST)

        msg.content = content
        msg.is_edited = True
        msg.edited_at = timezone.now()
        msg.save()
        return Response(MessageSerializer(msg).data, status=status.HTTP_200_OK)

#delete message
class DeleteMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            message = Message.objects.get(pk=pk, sender=request.user)
        except Message.DoesNotExist:
            return Response({"error": "Message not found or not yours"}, status=404)

        message.is_deleted = True
        message.content = "This message was deleted."
        message.save()

        return Response({"message": "Message deleted successfully"}, status=200)
    
class MarkReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        # find the message
        try:
            msg = Message.objects.get(pk=pk, receiver=request.user)
        except Message.DoesNotExist:
            return Response({"detail": "Message not found"}, status=status.HTTP_404_NOT_FOUND)

        # if not already read, mark it read
        if msg.read_at is None:
            msg.read_at = timezone.now()
            msg.save(update_fields=['read_at'])

        return Response({"read_at": msg.read_at})
    
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .models import Message
from .serializers import MessageSerializer
from django.contrib.auth import get_user_model
User = get_user_model()

class ThreadView(generics.ListCreateAPIView):
    """
    GET  /api/chat/thread/<username>/?page=1
    POST /api/chat/thread/<username>/
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        me = self.request.user
        other = get_object_or_404(User, username=self.kwargs['username'])
        return Message.objects.filter(
            Q(sender=me, receiver=other) | Q(sender=other, receiver=me)
        ).order_by('-timestamp')

    def perform_create(self, serializer):
        me = self.request.user
        other = get_object_or_404(User, username=self.kwargs['username'])
        # NOTE: receiver ko yahin set karte hain; client ko bhejne ki zarurat nahi
        serializer.save(sender=me, receiver=other)


class ConversationsView(APIView):
    """GET /api/chat/conversations/"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        me = request.user
        # sare users jinse mera messages ka exchange hua
        ids1 = Message.objects.filter(sender=me).values_list('receiver', flat=True)
        ids2 = Message.objects.filter(receiver=me).values_list('sender', flat=True)
        user_ids = set(list(ids1) + list(ids2))

        users = User.objects.filter(id__in=user_ids).exclude(id=me.id).distinct()
        data = []
        for u in users:
            last_msg = Message.objects.filter(
                Q(sender=me, receiver=u) | Q(sender=u, receiver=me)
            ).order_by('-timestamp').first()
            unread = Message.objects.filter(sender=u, receiver=me, read_at__isnull=True).count()
            data.append({
                "username": u.username,
                "last_message": last_msg.content if last_msg else None,
                "unread_count": unread,
            })
        # latest conversation top pe
        data.sort(key=lambda d: d["last_message"] or "", reverse=True)
        return Response(data, status=status.HTTP_200_OK)
    
# file upload
class FileUploadView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        # Save file
        path = default_storage.save(f'chat_files/{file.name}', file)
        file_url = request.build_absolute_uri('/media/' + path)

        return Response({'file_url': file_url}, status=201)