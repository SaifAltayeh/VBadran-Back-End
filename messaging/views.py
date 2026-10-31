from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Conversation, Message
from .serializers import MessageSerializer


class MessageThreadView(APIView):
    def get(self, request):
        conversation = Conversation.objects.filter(client=request.user).order_by("-updated_at").first()
        if conversation is None:
            return Response({"coach": {"name": "Badran", "avatar": "/images/dashboard/coach.jpg"}, "messages": []})
        return Response(
            {
                "coach": {"name": "Badran", "avatar": "/images/dashboard/coach.jpg"},
                "messages": MessageSerializer(conversation.messages.all(), many=True).data,
            }
        )

    def post(self, request):
        body = (request.data.get("body") or "").strip()
        if not body:
            return Response({"detail": "Write a message first."}, status=status.HTTP_400_BAD_REQUEST)
        conversation, _ = Conversation.objects.get_or_create(client=request.user)
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            body=body,
            is_coach=False,
        )
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
