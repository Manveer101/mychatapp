from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Message
from .serializers import MessageSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView



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
