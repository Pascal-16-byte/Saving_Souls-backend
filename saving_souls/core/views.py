from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics, status
from .models import Story, ChatMessage, ModerationLog
from .serializers import StorySerializer, ChatMessageSerializer
import os

# ------------------------------
# 🔹 Simple danger keyword list
# ------------------------------
DANGER_KEYWORDS = [
    "suicide", "kill myself", "end my life", "i can't go on",
    "i cant go on", "worthless", "no point", "want to die"
]


def check_danger(text):
    """Check if text contains danger keywords"""
    text = text.lower()
    return any(kw in text for kw in DANGER_KEYWORDS)


# ------------------------------
# 🔹 Optional AI integration
# ------------------------------
USE_OPENAI = os.getenv("USE_OPENAI", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


def generate_bot_reply(user_text, sentiment_label=None):
    """Generate chatbot reply (rule-based or via OpenAI if enabled)"""
    reply = f"I hear you. It sounds like you're feeling {sentiment_label or 'upset'}. I'm here to listen."

    if USE_OPENAI and OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            prompt = (
                "You are a compassionate, empathetic listener. "
                f"Respond supportively to: {user_text}"
            )
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            reply = res.choices[0].message.content.strip()
        except Exception as e:
            print("OpenAI API error:", e)

    return reply


# ------------------------------
# 🔹 Chatbot endpoint
# ------------------------------
class ChatbotAPI(APIView):
    """Handles chatbot communication"""
    def post(self, request):
        anon_id = request.data.get("anon_id", "guest")
        message = request.data.get("message", "")

        if not message:
            return Response({"error": "Message required"}, status=status.HTTP_400_BAD_REQUEST)

        # Save user message
        is_danger = check_danger(message)
        sentiment_label = "distressed" if is_danger else "neutral"

        ChatMessage.objects.create(
            anon_id=anon_id,
            message=message,
            role="user",
            sentiment=sentiment_label
        )

        # Crisis check
        if is_danger:
            bot_text = (
                "I’m really concerned. If you're thinking about harming yourself, "
                "please contact your local emergency services or a trusted person. "
                "Would you like me to show you some helpline resources?"
            )
            ChatMessage.objects.create(
                anon_id=anon_id,
                message=bot_text,
                role="bot",
                sentiment="serious"
            )
            crisis = {
                "alert": True,
                "message": "If you are in immediate danger, please contact local emergency services or a crisis helpline."
            }
            return Response({"reply": bot_text, "crisis": crisis})

        # Normal chat
        bot_reply = generate_bot_reply(message, sentiment_label)
        ChatMessage.objects.create(
            anon_id=anon_id,
            message=bot_reply,
            role="bot",
            sentiment=sentiment_label
        )
        return Response({"reply": bot_reply, "crisis": False})


# ------------------------------
# 🔹 Story Endpoints
# ------------------------------
class StoryCreateAPI(generics.CreateAPIView):
    serializer_class = StorySerializer

    def perform_create(self, serializer):
        content = serializer.validated_data.get("content", "")
        is_danger = check_danger(content)

        # Auto-flag stories containing dangerous content
        if is_danger:
            story = serializer.save(status="pending")
            ModerationLog.objects.create(
                story=story,
                reason="danger keyword detected",
                severity=0.95
            )
        else:
            serializer.save(status="approved")


class StoryListAPI(generics.ListAPIView):
    """Show only approved stories"""
    serializer_class = StorySerializer
    queryset = Story.objects.filter(status="approved").order_by("-created_at")


# ------------------------------
# 🔹 Moderation Endpoints
# ------------------------------
@api_view(["POST"])
def approve_story(request, story_id):
    """Approve flagged story"""
    try:
        story = Story.objects.get(id=story_id)
        story.status = "approved"
        story.save()
        return Response({"message": "Story approved"}, status=status.HTTP_200_OK)
    except Story.DoesNotExist:
        return Response({"error": "Story not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
def reject_story(request, story_id):
    """Reject flagged story"""
    try:
        story = Story.objects.get(id=story_id)
        story.status = "rejected"
        story.save()
        return Response({"message": "Story rejected"}, status=status.HTTP_200_OK)
    except Story.DoesNotExist:
        return Response({"error": "Story not found"}, status=status.HTTP_404_NOT_FOUND)
