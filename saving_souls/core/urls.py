from django.urls import path
# from .views import ChatbotAPI, StoryCreateAPI, StoryListAPI
from core import views

urlpatterns = [
    path("chatbot/", views.ChatbotAPI.as_view(), name="chatbot"),
    path("stories/", views.StoryListAPI.as_view(), name="stories-list"),
    path("stories/create/", views.StoryCreateAPI.as_view(), name="stories-create"),
    path("stories/<uuid:story_id>/approve/", views.approve_story, name="stories-approve"),
    path("stories/<uuid:story_id>/reject/", views.reject_story, name="stories-reject"),
]
