from rest_framework import serializers
from .models import Message
from django.contrib.auth.models import User

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)  # Show username instead of ID
    receiver = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='username')

    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['sender', 'timestamp']

