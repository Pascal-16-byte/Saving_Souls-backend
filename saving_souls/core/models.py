from django.db import models

# -------------------------------
#  Story Model
# -------------------------------
class Story(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    handle = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    anon_id = models.CharField(max_length=50, blank=True, null=True)  # <-- Add this

    def __str__(self):
        return f"Story #{self.id} by {self.handle or 'Anonymous'} ({self.status})"


# -------------------------------
#  Chat Message Model
# -------------------------------
class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ("user", "User"),
        ("bot", "Bot"),
    ]

    anon_id = models.CharField(max_length=100, default="guest")
    message = models.TextField()
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    sentiment = models.CharField(max_length=20, default="neutral")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.role}] {self.anon_id}: {self.message[:40]}..."


# -------------------------------
#  Moderation Log Model
# -------------------------------
class ModerationLog(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="moderation_logs")
    reason = models.CharField(max_length=200)
    severity = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ModerationLog #{self.id} → {self.story} | {self.reason} ({self.severity})"
