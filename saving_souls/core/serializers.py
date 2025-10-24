from rest_framework import serializers
from .models import Story, ChatMessage, ModerationLog

class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = "__all__"
        read_only_fields = ("id", "status", "sentiment", "created_at")

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = "__all__"
        read_only_fields = ("id", "sentiment", "created_at")

class ModerationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModerationLog
        fields = "__all__"
        read_only_fields = ("id", "created_at")
