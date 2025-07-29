from rest_framework import serializers
from .models import Message
from django.contrib.auth.models import User
from django.utils import timezone

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)
    receiver = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field='username')

    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['sender', 'timestamp', 'is_edited', 'edited_at', 'is_deleted']

    def update(self, instance, validated_data):
        # Only update the content field
        if 'content' in validated_data:
            instance.content = validated_data['content']
            instance.is_edited = True
            instance.edited_at = timezone.now()
            instance.save()
        return instance
