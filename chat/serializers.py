from rest_framework import serializers
from .models import Message, Reaction
from django.utils import timezone
from django.contrib.auth import get_user_model
User = get_user_model()

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)
    receiver = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
        required=False,          # <-- allow missing for thread POST
    )
    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['sender', 'timestamp', 'is_edited', 'edited_at', 'is_deleted', 'read_at', 'file', 'emoji']

    def update(self, instance, validated_data):
        # Only update the content field
        if 'content' in validated_data:
            instance.content = validated_data['content']
            instance.is_edited = True
            instance.edited_at = timezone.now()
            instance.save()
        return instance

class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ['id', 'user', 'emoji']