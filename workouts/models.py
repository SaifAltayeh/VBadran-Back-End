from django.conf import settings
from django.db import models

from programs.models import Program


class Exercise(models.Model):
    class Difficulty(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    name = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    video_url = models.CharField(max_length=500, blank=True)
    thumbnail = models.TextField(blank=True)
    image_alt = models.CharField(max_length=255, blank=True)
    muscle_group = models.CharField(max_length=80)
    difficulty = models.CharField(max_length=24, choices=Difficulty.choices, default=Difficulty.INTERMEDIATE)
    instructions = models.TextField(blank=True)
    tips = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class PortalVideo(models.Model):
    program = models.ForeignKey(Program, related_name="portal_videos", on_delete=models.CASCADE)
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    video_url = models.CharField(max_length=500)
    thumbnail = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class Workout(models.Model):
    title = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=45)
    focus = models.CharField(max_length=80, blank=True)
    coach_notes = models.TextField(blank=True)
    warmup = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.title


class WorkoutExercise(models.Model):
    workout = models.ForeignKey(Workout, related_name="items", on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, related_name="usages", on_delete=models.PROTECT)
    sets = models.CharField(max_length=40)
    reps = models.CharField(max_length=40)
    rest_seconds = models.PositiveIntegerField(default=90)
    tempo = models.CharField(max_length=40, blank=True)
    order = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.workout.title} · {self.exercise.name}"


class ProgramSchedule(models.Model):
    program = models.ForeignKey(Program, related_name="schedule", on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout, related_name="schedule_slots", null=True, blank=True, on_delete=models.SET_NULL)
    week_number = models.PositiveIntegerField()
    day_index = models.PositiveSmallIntegerField()
    day_label = models.CharField(max_length=16)
    is_rest = models.BooleanField(default=False)

    class Meta:
        ordering = ["week_number", "day_index"]
        unique_together = ("program", "week_number", "day_index")

    def __str__(self):
        return f"{self.program.title} W{self.week_number} {self.day_label}"


class WorkoutCompletion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="completions", on_delete=models.CASCADE)
    schedule = models.ForeignKey(ProgramSchedule, related_name="completions", on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "schedule")

    def __str__(self):
        return f"{self.user.email} · {self.schedule}"
