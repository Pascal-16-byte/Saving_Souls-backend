from django.contrib import admin
from .models import Story, ChatMessage, ModerationLog


# -------------------------------
# Story Admin
# -------------------------------
@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ("id", "handle", "country", "short_content", "status", "created_at")
    list_filter = ("status", "country", "created_at")
    search_fields = ("handle", "country", "content")
    ordering = ("-created_at",)
    actions = ["approve_stories", "reject_stories"]

    def short_content(self, obj):
        return (obj.content[:60] + "...") if len(obj.content) > 60 else obj.content
    short_content.short_description = "Content"

    # Custom actions for moderation
    def approve_stories(self, request, queryset):
        updated = queryset.update(status="approved")
        self.message_user(request, f"{updated} story(ies) approved successfully.")
    approve_stories.short_description = "Approve selected stories"

    def reject_stories(self, request, queryset):
        updated = queryset.update(status="rejected")
        self.message_user(request, f"{updated} story(ies) rejected successfully.")
    reject_stories.short_description = "Reject selected stories"


# -------------------------------
# Chat Message Admin
# -------------------------------
@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "anon_id", "role", "sentiment", "short_message", "created_at")
    list_filter = ("role", "sentiment", "created_at")
    search_fields = ("anon_id", "message")
    ordering = ("-created_at",)

    def short_message(self, obj):
        return (obj.message[:60] + "...") if len(obj.message) > 60 else obj.message
    short_message.short_description = "Message"


# -------------------------------
# Moderation Log Admin
# -------------------------------
@admin.register(ModerationLog)
class ModerationLogAdmin(admin.ModelAdmin):
    list_display = ("id", "story", "reason", "severity", "created_at")
    list_filter = ("reason", "severity", "created_at")
    search_fields = ("reason", "story__content")
    ordering = ("-created_at",)
