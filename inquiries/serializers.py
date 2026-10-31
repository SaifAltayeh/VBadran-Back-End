from rest_framework import serializers

from .models import ContactInquiry


class ContactInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInquiry
        fields = ["id", "name", "email", "phone", "goal", "fitness_level", "program", "message", "created_at"]
        read_only_fields = ["id", "created_at"]
