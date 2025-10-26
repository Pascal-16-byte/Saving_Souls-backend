from rest_framework import serializers
from .models import User, ChatbotSession, Post

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'country', 'age_confirmed', 'anonymous_handle', 'tier', 'chatbot_sessions', 'consent_given']
        extra_kwargs = {'password': {'write_only': True}}

class ChatbotSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotSession
        fields = ['id', 'prompt', 'response', 'timestamp']

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'content', 'anonymous', 'created_at']