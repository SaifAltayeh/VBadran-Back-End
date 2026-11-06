from rest_framework import serializers

from .models import Gym, Package, Program, ProgramFAQ, ProgramFeature


class GymSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gym
        fields = ["id", "name", "name_ar", "slug", "is_active", "order"]


class ProgramFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramFeature
        fields = ["id", "text", "text_ar"]


class ProgramFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramFAQ
        fields = ["id", "question", "question_ar", "answer", "answer_ar"]


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
            "title_ar",
            "slug",
            "short_description",
            "short_description_ar",
            "description",
            "description_ar",
            "price",
            "currency",
            "duration_weeks",
            "difficulty",
            "difficulty_label",
            "category",
            "category_label",
            "goal",
            "goal_ar",
            "featured_image",
            "image_alt",
            "is_featured",
            "includes_nutrition",
            "includes_training",
            "expected_outcome",
            "expected_outcome_ar",
            "who_for",
            "who_for_ar",
            "training_structure",
            "training_structure_ar",
            "nutrition_overview",
            "nutrition_overview_ar",
            "support_overview",
            "support_overview_ar",
            "features",
            "faqs",
        ]


class PackageSerializer(serializers.ModelSerializer):
    program_slug = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    gym = GymSerializer(read_only=True)

    class Meta:
        model = Package
        fields = [
            "id",
            "name",
            "name_ar",
            "slug",
            "tagline",
            "tagline_ar",
            "description",
            "description_ar",
            "duration_weeks",
            "price",
            "currency",
            "expected_outcome",
            "expected_outcome_ar",
            "is_highlighted",
            "program_slug",
            "support_label",
            "support_label_ar",
            "image",
            "image_alt",
            "gym",
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
