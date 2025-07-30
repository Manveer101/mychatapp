from rest_framework.viewsets import ModelViewSet
from django.db.models import Q, Max, Count
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Message
from .serializers import MessageSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework import generics, permissions, status
from django.utils import timezone



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

class SentMessagesView(ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user).order_by('-timestamp')
    
# edit message 
class EditMessageView(generics.UpdateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            message = Message.objects.get(pk=pk, sender=request.user)
        except Message.DoesNotExist:
            return Response({"error": "Message not found or not yours"}, status=404)

        content = request.data.get("content")
        if not content:
            return Response({"error": "No content provided"}, status=400)

        message.content = content
        message.is_edited = True
        message.edited_at = timezone.now()
        message.save()

        return Response({"message": "Message edited successfully"}, status=200)

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
from django.contrib.auth.models import User

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