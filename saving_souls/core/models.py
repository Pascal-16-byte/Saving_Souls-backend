import uuid
from django.db import models

class Story(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    anon_id = models.CharField(max_length=100)  # generated client-side or server-side
    content = models.TextField()
    sentiment = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

class ChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    anon_id = models.CharField(max_length=100)
    message = models.TextField()
    role = models.CharField(max_length=10)  # 'user' or 'bot'
    sentiment = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ModerationLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    story = models.ForeignKey(Story, null=True, on_delete=models.SET_NULL)
    reason = models.TextField()
    severity = models.FloatField(default=0.0)
    reviewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
