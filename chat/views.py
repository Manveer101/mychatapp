from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Message
from .serializers import MessageSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework import generics
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