from rest_framework import serializers

from .models import Package, Program, ProgramFAQ, ProgramFeature


class ProgramFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramFeature
        fields = ["id", "text"]


class ProgramFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramFAQ
        fields = ["id", "question", "answer"]


class ProgramSerializer(serializers.ModelSerializer):
    features = ProgramFeatureSerializer(many=True, read_only=True)
    faqs = ProgramFAQSerializer(many=True, read_only=True)
    category_label = serializers.CharField(source="get_category_display", read_only=True)
    difficulty_label = serializers.CharField(source="get_difficulty_display", read_only=True)

    class Meta:
        model = Program
        fields = [
            "id",
            "title",
            "slug",
            "short_description",
            "description",
            "price",
            "currency",
            "duration_weeks",
            "difficulty",
            "difficulty_label",
            "category",
            "category_label",
            "goal",
            "featured_image",
            "image_alt",
            "is_featured",
            "includes_nutrition",
            "includes_training",
            "expected_outcome",
            "who_for",
            "training_structure",
            "nutrition_overview",
            "support_overview",
            "features",
            "faqs",
        ]


class PackageSerializer(serializers.ModelSerializer):
    program_slug = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = [
            "id",
            "name",
            "slug",
            "tagline",
            "description",
            "duration_weeks",
            "price",
            "currency",
            "expected_outcome",
            "is_highlighted",
            "program_slug",
            "support_label",
            "features",
        ]

    def get_program_slug(self, obj):
        return obj.program.slug if obj.program_id else None

    def get_features(self, obj):
        return {
            "training_plan": obj.training_plan,
            "nutrition": obj.nutrition,
            "weekly_checkins": obj.weekly_checkins,
            "video_library": obj.video_library,
            "coach_support": obj.coach_support,
            "progress_tracking": obj.progress_tracking,
            "program_adjustments": obj.program_adjustments,
            "messaging": obj.messaging,
        }
