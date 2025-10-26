from django.urls import path
from .views import OnboardingView, ChatbotSessionView, PostView

urlpatterns = [
    path('onboarding/', OnboardingView.as_view(), name='onboarding'),
    path('chatbot/', ChatbotSessionView.as_view(), name='chatbot'),
    path('posts/', PostView.as_view(), name='posts'),
]