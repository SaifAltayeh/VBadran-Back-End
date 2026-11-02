from rest_framework import serializers

from .models import Exercise, PortalVideo, Workout, WorkoutExercise


class ExerciseSerializer(serializers.ModelSerializer):
    difficulty_label = serializers.CharField(source="get_difficulty_display", read_only=True)

    class Meta:
        model = Exercise
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "video_url",
            "thumbnail",
            "image_alt",
            "muscle_group",
            "difficulty",
            "difficulty_label",
            "instructions",
            "tips",
        ]


class PortalVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortalVideo
        fields = ["id", "title", "description", "video_url", "thumbnail", "order"]


class WorkoutExerciseSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)

    class Meta:
        model = WorkoutExercise
        fields = ["id", "order", "sets", "reps", "rest_seconds", "tempo", "notes", "exercise"]


class WorkoutSerializer(serializers.ModelSerializer):
    exercises = WorkoutExerciseSerializer(source="items", many=True, read_only=True)

    class Meta:
        model = Workout
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "duration_minutes",
            "focus",
            "coach_notes",
            "warmup",
            "exercises",
        ]
