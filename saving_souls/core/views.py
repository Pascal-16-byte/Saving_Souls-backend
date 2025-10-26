from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import User, ChatbotSession, Post
from .serializers import UserSerializer, ChatbotSessionSerializer, PostSerializer
from datetime import timedelta
from django.utils import timezone
import requests  # For external moderation if needed

class OnboardingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(consent_given=True)
            # Generate anonymous handle if not provided
            if not user.anonymous_handle:
                user.anonymous_handle = f'anon_{user.id}'
                user.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChatbotSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.tier < 1 or not user.consent_given:
            return Response({'error': 'Complete onboarding first'}, status=status.HTTP_403_FORBIDDEN)
        
        prompt = request.data.get('prompt', 'Provide a journaling prompt or coping exercise.')
        response = self.generate_chatbot_response(prompt)  # Implement bot logic
        
        session = ChatbotSession.objects.create(user=user, prompt=prompt, response=response)
        user.chatbot_sessions += 1
        user.last_session_time = timezone.now()
        
        # Tier progression: After 3-7 sessions, or after a cooldown (e.g., 1 day)
        if user.chatbot_sessions >= 3 and (user.chatbot_sessions <= 7 or (user.last_session_time - timezone.now() > timedelta(days=1))):
            user.tier = 2
        user.save()
        
        return Response(ChatbotSessionSerializer(session).data)

    def generate_chatbot_response(self, prompt):
        # Simple rule-based bot (expand with OpenAI API for real use)
        if 'journal' in prompt.lower():
            return "Journal prompt: Write about three things you're grateful for today."
        elif 'coping' in prompt.lower():
            return "Coping exercise: Practice 4-7-8 breathing: Inhale for 4s, hold for 7s, exhale for 8s."
        return "Tell me more about how you're feeling."

class PostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.tier < 2:
            return Response({'error': 'Unlock Tier 2 by completing chatbot sessions'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            content = serializer.validated_data['content']
            if not self.moderate_content(content):
                return Response({'error': 'Content failed moderation. Please revise.'}, status=status.HTTP_400_BAD_REQUEST)
            
            post = serializer.save(user=user, moderated=True, published=True)
            return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        posts = Post.objects.filter(published=True).order_by('-created_at')
        return Response(PostSerializer(posts, many=True).data)

    def moderate_content(self, content):
        # Basic keyword filter (expand with external API)
        bad_keywords = ['harm', 'suicide', 'violence']  # Customize
        if any(word in content.lower() for word in bad_keywords):
            return False
        # Example external call (uncomment and add API key)
        # response = requests.post('https://api.moderatecontent.com/text/', data={'key': 'YOUR_KEY', 'text': content})
        # if response.json().get('rating_label') == 'adult':
        #     return False
        return True