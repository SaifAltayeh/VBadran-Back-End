from urllib.parse import urlparse

from django.conf import settings
from rest_framework import serializers

from accounts.models import User
from inquiries.models import ContactInquiry
from nutrition.models import Meal, NutritionDay, NutritionNote, NutritionPlan
from payments.models import Subscription
from programs.models import Gym, Package, Program
from testimonials.models import Testimonial
from transformations.models import Transformation
from workouts.models import Exercise, MemberPlan, PortalVideo, ProgramSchedule, Workout, WorkoutExercise

ALLOWED_VIDEO_HOSTS = (
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
    "vimeo.com",
    "www.vimeo.com",
    "player.vimeo.com",
)


def validate_video_source(value: str) -> str:
    url = (value or "").strip()
    if not url:
        raise serializers.ValidationError("Add a video file or a hosted video URL.")
    if url.startswith("data:video/"):
        if settings.DEBUG and not getattr(settings, "ON_VERCEL", False):
            return url
        raise serializers.ValidationError("Data URLs are not production video storage. Use a YouTube, Vimeo, or MP4 URL.")
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme in {"http", "https"} and (
        host in ALLOWED_VIDEO_HOSTS or host.endswith(".youtube.com") or host.endswith(".vimeo.com")
    ):
        return url
    if parsed.scheme in {"http", "https"} and url.lower().endswith((".mp4", ".webm", ".mov", ".m4v")):
        return url
    if url.startswith("/media/") and url.lower().endswith((".mp4", ".webm", ".mov", ".m4v")):
        return url
    raise serializers.ValidationError("Use YouTube, Vimeo, or a direct MP4/WebM URL.")


class ProgramAdminSerializer(serializers.ModelSerializer):
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
            "category",
            "goal",
            "goal_ar",
            "featured_image",
            "image_alt",
            "is_featured",
            "is_active",
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
        ]

    def validate_slug(self, value):
        slug = (value or "").strip()
        if not slug:
            raise serializers.ValidationError("Slug is required.")
        qs = Program.objects.filter(slug=slug)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("This slug is already used. Choose another.")
        return slug

    def validate_category(self, value):
        allowed = {choice for choice, _ in Program.Category.choices}
        if value not in allowed:
            raise serializers.ValidationError(
                f"Use one of: {', '.join(sorted(allowed))}."
            )
        return value

    def validate(self, attrs):
        title = attrs.get("title") or getattr(self.instance, "title", "") or "Program"
        for field in ("short_description", "description", "goal"):
            if field in attrs and not str(attrs.get(field) or "").strip():
                attrs[field] = title
        if "duration_weeks" in attrs and attrs.get("duration_weeks") in ("", 0):
            attrs["duration_weeks"] = None
        if "price" in attrs and attrs.get("price") in (None, ""):
            attrs["price"] = 0
        return attrs


class GymAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gym
        fields = ["id", "name", "name_ar", "slug", "is_active", "order"]


class PackageAdminSerializer(serializers.ModelSerializer):
    gym_name = serializers.CharField(source="gym.name", read_only=True)

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
            "program",
            "gym",
            "gym_name",
            "image",
            "image_alt",
            "support_label",
            "support_label_ar",
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

    def validate(self, attrs):
        if attrs.get("duration_weeks") in ("", 0):
            attrs["duration_weeks"] = None
        return attrs


class TransformationAdminSerializer(serializers.ModelSerializer):
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
            "program",
            "program_name",
            "program_name_ar",
            "story",
            "story_ar",
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
    goal = serializers.CharField(source="profile.goal", required=False, allow_blank=True)
    gym = serializers.IntegerField(source="profile.gym_id", required=False, allow_null=True)
    gym_name = serializers.CharField(source="profile.gym.name", read_only=True, default="")
    package_name = serializers.SerializerMethodField()
    assigned_workout = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    assigned_plan = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_active",
            "date_joined",
            "phone",
            "goal",
            "gym",
            "gym_name",
            "package_name",
            "assigned_workout",
            "assigned_plan",
        ]
        read_only_fields = ["email", "is_staff", "is_active", "date_joined", "phone", "gym_name", "package_name", "assigned_plan"]

    def get_package_name(self, obj):
        sub = obj.subscriptions.filter(status=Subscription.Status.ACTIVE).select_related("package").first()
        if sub and sub.package_id:
            return sub.package.name
        if sub and sub.program_id:
            return sub.program.title
        return ""

    def get_assigned_plan(self, obj):
        plan = obj.member_plans.filter(is_active=True).select_related("workout").first()
        if not plan:
            return None
        return {"id": plan.id, "workout_id": plan.workout_id, "workout_title": plan.workout.title, "notes": plan.notes}

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", {})
        assigned = validated_data.pop("assigned_workout", serializers.empty)
        notes = self.context["request"].data.get("plan_notes", "") if self.context.get("request") else ""
        super().update(instance, validated_data)
        profile = instance.profile
        if "goal" in profile_data:
            profile.goal = profile_data["goal"]
        if "gym_id" in profile_data:
            profile.gym_id = profile_data["gym_id"]
        profile.save()
        if assigned is not serializers.empty:
            instance.member_plans.filter(is_active=True).update(is_active=False)
            if assigned:
                MemberPlan.objects.create(user=instance, workout_id=assigned, notes=notes or "", is_active=True)
        return instance


class ExerciseAdminSerializer(serializers.ModelSerializer):
    package_ids = serializers.PrimaryKeyRelatedField(
        source="packages",
        many=True,
        queryset=Package.objects.all(),
        required=False,
    )
    package_names = serializers.SerializerMethodField()

    class Meta:
        model = Exercise
        fields = [
            "id",
            "name",
            "name_ar",
            "slug",
            "description",
            "description_ar",
            "video_url",
            "thumbnail",
            "image_alt",
            "muscle_group",
            "difficulty",
            "instructions",
            "instructions_ar",
            "tips",
            "tips_ar",
            "package_ids",
            "package_names",
            "is_active",
        ]
        read_only_fields = ["package_names"]

    def get_package_names(self, obj):
        return [package.name for package in obj.packages.all()]

    def validate_video_url(self, value):
        if not (value or "").strip():
            return value
        return validate_video_source(value)


class PortalVideoAdminSerializer(serializers.ModelSerializer):
    program_title = serializers.CharField(source="program.title", read_only=True, default="")
    gym_name = serializers.CharField(source="gym.name", read_only=True, default="")
    package_ids = serializers.PrimaryKeyRelatedField(
        source="packages",
        many=True,
        queryset=Package.objects.all(),
        required=False,
    )
    package_names = serializers.SerializerMethodField()

    class Meta:
        model = PortalVideo
        fields = [
            "id",
            "program",
            "program_title",
            "package_ids",
            "package_names",
            "gym",
            "gym_name",
            "title",
            "title_ar",
            "description",
            "description_ar",
            "video_url",
            "thumbnail",
            "order",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "program_title", "gym_name", "package_names"]

    def get_package_names(self, obj):
        return [package.name for package in obj.packages.all()]

    def validate_video_url(self, value):
        return validate_video_source(value)


class WorkoutItemWriteSerializer(serializers.Serializer):
    exercise_id = serializers.IntegerField()
    sets = serializers.CharField(max_length=40, required=False, allow_blank=True, default="3")
    reps = serializers.CharField(max_length=40, required=False, allow_blank=True, default="10")
    rest_seconds = serializers.IntegerField(required=False, default=90)
    tempo = serializers.CharField(max_length=40, required=False, allow_blank=True, default="")
    notes = serializers.CharField(required=False, allow_blank=True, default="")
    order = serializers.IntegerField(required=False, default=0)


class WorkoutAdminSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    item_rows = WorkoutItemWriteSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Workout
        fields = [
            "id",
            "title",
            "title_ar",
            "slug",
            "description",
            "description_ar",
            "duration_minutes",
            "focus",
            "focus_ar",
            "coach_notes",
            "coach_notes_ar",
            "warmup",
            "warmup_ar",
            "items",
            "item_rows",
        ]

    def get_items(self, obj):
        return [
            {
                "id": row.id,
                "exercise_id": row.exercise_id,
                "exercise_name": row.exercise.name,
                "sets": row.sets,
                "reps": row.reps,
                "rest_seconds": row.rest_seconds,
                "tempo": row.tempo,
                "notes": row.notes,
                "order": row.order,
            }
            for row in obj.items.select_related("exercise").all()
        ]

    def _sync_items(self, workout, rows):
        workout.items.all().delete()
        for index, row in enumerate(rows or []):
            exercise = Exercise.objects.filter(pk=row["exercise_id"]).first()
            if not exercise:
                continue
            WorkoutExercise.objects.create(
                workout=workout,
                exercise=exercise,
                sets=row.get("sets") or "3",
                reps=row.get("reps") or "10",
                rest_seconds=row.get("rest_seconds") or 90,
                tempo=row.get("tempo") or "",
                notes=row.get("notes") or "",
                order=row.get("order") if row.get("order") is not None else index,
            )

    def create(self, validated_data):
        rows = validated_data.pop("item_rows", [])
        workout = Workout.objects.create(**validated_data)
        self._sync_items(workout, rows)
        return workout

    def update(self, instance, validated_data):
        rows = validated_data.pop("item_rows", None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if rows is not None:
            self._sync_items(instance, rows)
        return instance


class ScheduleAdminSerializer(serializers.ModelSerializer):
    program_title = serializers.CharField(source="program.title", read_only=True)
    workout_title = serializers.CharField(source="workout.title", read_only=True, allow_null=True)

    class Meta:
        model = ProgramSchedule
        fields = [
            "id",
            "program",
            "program_title",
            "workout",
            "workout_title",
            "week_number",
            "day_index",
            "day_label",
            "is_rest",
        ]


class NutritionMealWriteSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=80)
    suggestion = serializers.CharField()
    order = serializers.IntegerField(required=False, default=0)


class NutritionDayWriteSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=80)
    order = serializers.IntegerField(required=False, default=0)
    meals = NutritionMealWriteSerializer(many=True, required=False)


class NutritionPlanAdminSerializer(serializers.ModelSerializer):
    program_title = serializers.CharField(source="program.title", read_only=True)
    days = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()
    day_rows = NutritionDayWriteSerializer(many=True, write_only=True, required=False)
    note_rows = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)

    class Meta:
        model = NutritionPlan
        fields = [
            "id",
            "program",
            "program_title",
            "title",
            "overview",
            "calories",
            "protein_g",
            "carbs_g",
            "fats_g",
            "coach_notes",
            "download_label",
            "download_url",
            "days",
            "notes",
            "day_rows",
            "note_rows",
        ]

    def get_days(self, obj):
        return [
            {
                "id": day.id,
                "name": day.name,
                "order": day.order,
                "meals": [
                    {"id": meal.id, "name": meal.name, "suggestion": meal.suggestion, "order": meal.order}
                    for meal in day.meals.all()
                ],
            }
            for day in obj.days.prefetch_related("meals").all()
        ]

    def get_notes(self, obj):
        return [{"id": note.id, "body": note.body, "order": note.order} for note in obj.notes.all()]

    def _sync_days(self, plan, day_rows):
        plan.days.all().delete()
        for index, day in enumerate(day_rows or []):
            created = NutritionDay.objects.create(
                plan=plan,
                name=day.get("name") or f"Day {index + 1}",
                order=day.get("order") if day.get("order") is not None else index,
            )
            for meal_index, meal in enumerate(day.get("meals") or []):
                Meal.objects.create(
                    day=created,
                    name=meal.get("name") or f"Meal {meal_index + 1}",
                    suggestion=meal.get("suggestion") or "",
                    order=meal.get("order") if meal.get("order") is not None else meal_index,
                )

    def _sync_notes(self, plan, note_rows):
        plan.notes.all().delete()
        for index, body in enumerate(note_rows or []):
            text = str(body or "").strip()
            if not text:
                continue
            NutritionNote.objects.create(plan=plan, body=text, order=index)

    def create(self, validated_data):
        day_rows = validated_data.pop("day_rows", [])
        note_rows = validated_data.pop("note_rows", [])
        plan = NutritionPlan.objects.create(**validated_data)
        self._sync_days(plan, day_rows)
        self._sync_notes(plan, note_rows)
        return plan

    def update(self, instance, validated_data):
        day_rows = validated_data.pop("day_rows", None)
        note_rows = validated_data.pop("note_rows", None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if day_rows is not None:
            self._sync_days(instance, day_rows)
        if note_rows is not None:
            self._sync_notes(instance, note_rows)
        return instance


class SubscriptionAdminSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.SerializerMethodField()
    program_title = serializers.CharField(source="program.title", read_only=True, default="")
    package_name = serializers.CharField(source="package.name", read_only=True, default="")
    gym_name = serializers.CharField(source="gym.name", read_only=True, default="")

    class Meta:
        model = Subscription
        fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "program",
            "program_title",
            "package",
            "package_name",
            "gym",
            "gym_name",
            "order",
            "status",
            "start_date",
            "end_date",
            "coach_note",
            "created_at",
        ]
        read_only_fields = ["created_at", "user_email", "user_name", "program_title", "package_name", "gym_name"]

    def get_user_name(self, obj):
        return (f"{obj.user.first_name} {obj.user.last_name}").strip() or obj.user.email


class MemberPlanAdminSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    workout_title = serializers.CharField(source="workout.title", read_only=True)

    class Meta:
        model = MemberPlan
        fields = [
            "id",
            "user",
            "user_email",
            "workout",
            "workout_title",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "user_email", "workout_title"]

    def create(self, validated_data):
        if validated_data.get("is_active", True):
            MemberPlan.objects.filter(user=validated_data["user"], is_active=True).update(is_active=False)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get("is_active", instance.is_active):
            MemberPlan.objects.filter(user=instance.user, is_active=True).exclude(pk=instance.pk).update(is_active=False)
        return super().update(instance, validated_data)
