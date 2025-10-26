from rest_framework import serializers
from .models import Story, ChatMessage, ModerationLog

# ------------------------------
# 🔹 Story Serializer
# ------------------------------
class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ['id', 'anon_id', 'content', 'created_at', 'status']


# ------------------------------
# 🔹 Chat Message Serializer
# ------------------------------
class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'anon_id', 'message', 'role', 'sentiment', 'created_at']


# ------------------------------
# 🔹 Moderation Log Serializer
# ------------------------------
class ModerationLogSerializer(serializers.ModelSerializer):
    story = StorySerializer(read_only=True)

    class Meta:
        model = ModerationLog
        fields = ['id', 'story', 'reason', 'severity', 'created_at']
