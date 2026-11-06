from rest_framework import serializers

from .models import Transformation


class TransformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transformation
        fields = [
            "id",
            "client_name",
            "client_name_ar",
            "slug",
            "before_image",
            "after_image",
            "cover_image",
            "image_alt",
            "duration_weeks",
            "result_summary",
            "result_summary_ar",
            "program_name",
            "program_name_ar",
            "story",
            "story_ar",
            "is_featured",
        ]
