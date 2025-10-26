from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    country = models.CharField(max_length=100, blank=True)
    age_confirmed = models.BooleanField(default=False)
    anonymous_handle = models.CharField(max_length=50, blank=True, null=True)
    tier = models.IntegerField(default=1)
    chatbot_sessions = models.IntegerField(default=0)
    consent_given = models.BooleanField(default=False)
    last_session_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username or self.anonymous_handle or 'Anonymous'

class ChatbotSession(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    prompt = models.TextField(blank=True)
    response = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session for {self.user} at {self.timestamp}"

class Post(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    content = models.TextField()
    anonymous = models.BooleanField(default=True)
    moderated = models.BooleanField(default=False)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.user} at {self.created_at}"