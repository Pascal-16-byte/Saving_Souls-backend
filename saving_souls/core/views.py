from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics, status
from .models import Story, ChatMessage, ModerationLog
from .serializers import StorySerializer, ChatMessageSerializer
from django.conf import settings
import os, re, requests

# Simple rule-based "danger" detection (MVP)
DANGER_KEYWORDS = [
    "suicide","kill myself","end my life","i can't go on","i cant go on",
    "worthless","no point","want to die"
]

def check_danger(text):
    t = text.lower()
    for kw in DANGER_KEYWORDS:
        if kw in t:
            return True
    return False

# Optional: call OpenAI for more empathetic reply (set OPENAI_API_KEY in .env)
USE_OPENAI = os.getenv("USE_OPENAI", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

def generate_bot_reply(user_text, sentiment_label=None):
    # Simple default reply
    reply = f"I hear you. It sounds like you're feeling {sentiment_label or 'upset'}. I'm here to listen."
    # Optional: use OpenAI for better replies
    if USE_OPENAI and OPENAI_API_KEY:
        import openai
        openai.api_key = OPENAI_API_KEY
        prompt = f"You are a compassionate, empathetic listener. Respond supportively to: {user_text}"
        try:
            res = openai.ChatCompletion.create(
                model="gpt-4o-mini",  # change if needed
                messages=[{"role":"user","content":prompt}],
                temperature=0.7,
                max_tokens=200
            )
            reply = res['choices'][0]['message']['content'].strip()
        except Exception as e:
            print("OpenAI error:", e)
    return reply

class ChatbotAPI(APIView):
    def post(self, request):
        anon_id = request.data.get("anon_id", "guest")
        text = request.data.get("message", "")
        if not text:
            return Response({"error":"message required"}, status=status.HTTP_400_BAD_REQUEST)

        # (Optional) simple sentiment label: naive
        sentiment_label = "distressed" if check_danger(text) else "neutral"

        # store user message
        um = ChatMessage.objects.create(anon_id=anon_id, message=text, role="user", sentiment=sentiment_label)

        # if danger detected, return crisis info immediately
        if check_danger(text):
            crisis = {
                "alert": True,
                "message": "If you are in immediate danger, please contact local emergency services or a crisis line. Here is a helpline you can try: [insert local helpline]."
            }
            bot_text = "I’m really concerned. If you're thinking about harming yourself, please contact your local emergency services right now. Would you like resources?"
            bm = ChatMessage.objects.create(anon_id=anon_id, message=bot_text, role="bot", sentiment="serious")
            return Response({"reply": bot_text, "crisis": crisis})

        # generate a reply
        bot_reply = generate_bot_reply(text, sentiment_label)
        bm = ChatMessage.objects.create(anon_id=anon_id, message=bot_reply, role="bot", sentiment=sentiment_label)
        return Response({"reply": bot_reply, "crisis": False})

# Stories
class StoryCreateAPI(generics.CreateAPIView):
    serializer_class = StorySerializer
    def perform_create(self, serializer):
        content = serializer.validated_data.get("content", "")
        # naive moderation: if contains dangerous keywords -> flag and create moderation log
        severity = 0.0
        for kw in DANGER_KEYWORDS:
            if kw in content.lower():
                severity = 0.95
                break
        instance = serializer.save(status="pending") if severity >= 0.5 else serializer.save(status="approved")
        if severity >= 0.5:
            ModerationLog.objects.create(story=instance, reason="danger keyword detected", severity=severity)

class StoryListAPI(generics.ListAPIView):
    serializer_class = StorySerializer
    queryset = Story.objects.filter(status="approved").order_by("-created_at")

@api_view(["POST"])
def approve_story(request, story_id):
    try:
        story = Story.objects.get(id=story_id)
        story.status = "approved"
        story.save()
        return Response({"message": "Story approved"}, status=status.HTTP_200_OK)
    except Story.DoesNotExist:
        return Response({"error": "Story not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(["POST"])
def reject_story(request, story_id):
    try:
        story = Story.objects.get(id=story_id)
        story.status = "rejected"
        story.save()
        return Response({"message": "Story rejected"}, status=status.HTTP_200_OK)
    except Story.DoesNotExist:
        return Response({"error": "Story not found"}, status=status.HTTP_404_NOT_FOUND)
