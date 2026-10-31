from rest_framework import serializers

from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "body", "is_coach", "created_at"]
        read_only_fields = ["id", "is_coach", "created_at"]
