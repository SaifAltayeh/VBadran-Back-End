from rest_framework import serializers

from accounts.models import User
from inquiries.models import ContactInquiry
from programs.models import Package, Program
from testimonials.models import Testimonial
from transformations.models import Transformation


class ProgramAdminSerializer(serializers.ModelSerializer):
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
            "category",
            "goal",
            "featured_image",
            "image_alt",
            "is_featured",
            "is_active",
            "includes_nutrition",
            "includes_training",
            "expected_outcome",
            "who_for",
            "training_structure",
            "nutrition_overview",
            "support_overview",
        ]


class PackageAdminSerializer(serializers.ModelSerializer):
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
            "program",
            "support_label",
            "training_plan",
            "nutrition",
            "weekly_checkins",
            "video_library",
            "coach_support",
            "progress_tracking",
            "program_adjustments",
            "messaging",
            "order",
            "is_active",
        ]


class TransformationAdminSerializer(serializers.ModelSerializer):
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
            "program",
            "program_name",
            "story",
            "is_featured",
            "order",
        ]


class TestimonialAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ["id", "client_name", "photo", "quote", "program_name", "rating", "is_featured", "order"]


class InquiryAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInquiry
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "goal",
            "fitness_level",
            "program",
            "message",
            "status",
            "created_at",
        ]
        read_only_fields = ["name", "email", "phone", "goal", "fitness_level", "program", "message", "created_at"]


class ClientAdminSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source="profile.phone", read_only=True)
    goal = serializers.CharField(source="profile.goal", read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "is_staff", "is_active", "date_joined", "phone", "goal"]
        read_only_fields = fields
