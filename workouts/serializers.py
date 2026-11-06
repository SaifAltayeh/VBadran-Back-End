from rest_framework import serializers

from programs.serializers import GymSerializer

from .models import Exercise, MemberPlan, PortalVideo, Workout, WorkoutExercise

PACKAGE_COVER_SLUGS = ("spark", "platinum", "oxygen")


def cover_for_package(package):
    if package is None:
        return ""
    candidates = [getattr(package, "slug", "")]
    gym = getattr(package, "gym", None)
    if gym is not None:
        candidates.append(getattr(gym, "slug", ""))
    for slug in candidates:
        if slug in PACKAGE_COVER_SLUGS:
            return f"/images/packages/{slug}-cover.jpg"
    return ""


class ExerciseSerializer(serializers.ModelSerializer):
    difficulty_label = serializers.CharField(source="get_difficulty_display", read_only=True)
    thumbnail = serializers.SerializerMethodField()

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
            "difficulty_label",
            "instructions",
            "instructions_ar",
            "tips",
            "tips_ar",
            "is_active",
        ]

    def get_thumbnail(self, obj):
        package = self.context.get("member_package")
        packages = list(obj.packages.all())
        if package is not None and len(packages) > 1:
            cover = cover_for_package(package)
            if cover:
                return cover
        return obj.thumbnail


class PortalVideoSerializer(serializers.ModelSerializer):
    gym = GymSerializer(read_only=True)
    package_ids = serializers.PrimaryKeyRelatedField(source="packages", many=True, read_only=True)

    class Meta:
        model = PortalVideo
        fields = [
            "id",
            "title",
            "title_ar",
            "description",
            "description_ar",
            "video_url",
            "thumbnail",
            "order",
            "gym",
            "package_ids",
        ]


class WorkoutExerciseSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)

    class Meta:
        model = WorkoutExercise
        fields = ["id", "order", "sets", "reps", "rest_seconds", "tempo", "notes", "notes_ar", "exercise"]


class WorkoutSerializer(serializers.ModelSerializer):
    exercises = WorkoutExerciseSerializer(source="items", many=True, read_only=True)

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
            "exercises",
        ]


class MemberPlanSerializer(serializers.ModelSerializer):
    workout = WorkoutSerializer(read_only=True)

    class Meta:
        model = MemberPlan
        fields = ["id", "workout", "notes", "is_active", "created_at", "updated_at"]
