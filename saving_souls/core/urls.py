from django.urls import path
from .views import (
    ChatbotAPI,
    StoryCreateAPI,
    StoryListAPI,
    approve_story,
    reject_story,
)

urlpatterns = [
    # Chatbot
    path('chat/', ChatbotAPI.as_view(), name='chatbot'),

    # Stories
    path('stories/', StoryListAPI.as_view(), name='story-list'),
    path('stories/create/', StoryCreateAPI.as_view(), name='story-create'),

    # Moderation
    path('stories/<int:story_id>/approve/', approve_story, name='approve-story'),
    path('stories/<int:story_id>/reject/', reject_story, name='reject-story'),
]
