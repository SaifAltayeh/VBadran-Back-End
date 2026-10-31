from rest_framework import serializers

from .models import Transformation


class TransformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transformation
        fields = [
            "id",
            "client_name",
            "slug",
            "before_image",
            "after_image",
            "cover_image",
            "image_alt",
            "duration_weeks",
            "result_summary",
            "program_name",
            "story",
            "is_featured",
        ]
