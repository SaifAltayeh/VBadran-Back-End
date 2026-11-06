from django.contrib import admin

from .models import Exercise, MemberPlan, PortalVideo, ProgramSchedule, Workout, WorkoutCompletion, WorkoutExercise


class WorkoutExerciseInline(admin.TabularInline):
    model = WorkoutExercise
    extra = 1


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name", "muscle_group", "difficulty", "is_active")
    list_filter = ("muscle_group", "difficulty", "is_active")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(PortalVideo)
class PortalVideoAdmin(admin.ModelAdmin):
    list_display = ("title", "program", "gym", "order", "is_active")
    list_filter = ("program", "gym", "is_active")
    filter_horizontal = ("packages",)
    search_fields = ("title", "video_url")


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ("title", "focus", "duration_minutes")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [WorkoutExerciseInline]


@admin.register(ProgramSchedule)
class ProgramScheduleAdmin(admin.ModelAdmin):
    list_display = ("program", "week_number", "day_label", "workout", "is_rest")
    list_filter = ("program", "is_rest", "week_number")


@admin.register(WorkoutCompletion)
class WorkoutCompletionAdmin(admin.ModelAdmin):
    list_display = ("user", "schedule", "completed_at")
    search_fields = ("user__email",)


@admin.register(MemberPlan)
class MemberPlanAdmin(admin.ModelAdmin):
    list_display = ("user", "workout", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("user__email", "workout__title")
