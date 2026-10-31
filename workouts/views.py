from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Exercise, ProgramSchedule, Workout, WorkoutCompletion
from .serializers import ExerciseSerializer, WorkoutSerializer


class ExerciseViewSet(ReadOnlyModelViewSet):
    serializer_class = ExerciseSerializer
    lookup_field = "slug"
    filterset_fields = ["muscle_group", "difficulty"]
    queryset = Exercise.objects.all()


class WorkoutViewSet(ReadOnlyModelViewSet):
    serializer_class = WorkoutSerializer
    queryset = Workout.objects.prefetch_related("items__exercise")

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
