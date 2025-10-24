from django.contrib import admin
from .models import Story, ChatMessage, ModerationLog

admin.site.register(Story)
admin.site.register(ChatMessage)
admin.site.register(ModerationLog)
