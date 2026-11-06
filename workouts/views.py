from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from dashboard.services import active_plan_for, subscription_for

from .models import Exercise, ProgramSchedule, Workout, WorkoutCompletion
from .serializers import ExerciseSerializer, WorkoutSerializer


def member_workout_ids(user):
    plan = active_plan_for(user)
    ids = set()
    if plan:
        ids.add(plan.workout_id)
    subscription = subscription_for(user)
    if subscription and subscription.program_id:
        ids.update(
            ProgramSchedule.objects.filter(program=subscription.program, workout_id__isnull=False).values_list(
                "workout_id",
                flat=True,
            )
        )
    return ids


class ExerciseViewSet(ReadOnlyModelViewSet):
    serializer_class = ExerciseSerializer
    lookup_field = "slug"
    filterset_fields = ["muscle_group", "difficulty"]

    def get_queryset(self):
        subscription = subscription_for(self.request.user)
        if not (subscription and subscription.package_id):
            return Exercise.objects.none()
        return (
            Exercise.objects.filter(is_active=True, packages=subscription.package)
            .exclude(video_url="")
            .prefetch_related("packages")
            .distinct()
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        subscription = subscription_for(self.request.user)
        context["member_package"] = subscription.package if subscription else None
        return context


class WorkoutViewSet(ReadOnlyModelViewSet):
    serializer_class = WorkoutSerializer

    def get_queryset(self):
        return Workout.objects.filter(id__in=member_workout_ids(self.request.user)).prefetch_related("items__exercise")

    @action(detail=False, methods=["post"], url_path="complete")
    def complete(self, request):
        schedule_id = request.data.get("schedule_id")
        slot = ProgramSchedule.objects.filter(
            pk=schedule_id,
            program__subscriptions__user=request.user,
        ).first()
        if slot is None or slot.is_rest:
            return Response({"detail": "That session could not be updated."}, status=status.HTTP_400_BAD_REQUEST)
        WorkoutCompletion.objects.get_or_create(user=request.user, schedule=slot)
        return Response({"status": "completed", "schedule_id": slot.id})
