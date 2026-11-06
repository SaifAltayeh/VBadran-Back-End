from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.services import active_plan_for, subscription_for

from .models import PortalVideo
from .serializers import MemberPlanSerializer, PortalVideoSerializer, WorkoutSerializer


class MyPortalVideosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subscription = subscription_for(request.user)
        if subscription is None:
            return Response({"videos": [], "program": None, "package": None})
        filters = Q()
        if subscription.package_id:
            filters |= Q(packages=subscription.package)
        if subscription.program_id:
            filters |= Q(program=subscription.program)
        if subscription.gym_id:
            filters |= Q(gym=subscription.gym, packages__isnull=True, program__isnull=True)
        if not filters:
            return Response({"videos": [], "program": None, "package": None})
        videos = (
            PortalVideo.objects.filter(is_active=True)
            .filter(filters)
            .select_related("gym", "program")
            .prefetch_related("packages")
            .distinct()
        )
        program = None
        if subscription.program_id:
            program = {"id": subscription.program_id, "title": subscription.program.title, "title_ar": subscription.program.title_ar}
        package = None
        if subscription.package_id:
            package = {
                "id": subscription.package_id,
                "name": subscription.package.name,
                "name_ar": subscription.package.name_ar,
                "slug": subscription.package.slug,
            }
        return Response(
            {
                "program": program,
                "package": package,
                "videos": PortalVideoSerializer(videos, many=True).data,
            }
        )


class MyPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plan = active_plan_for(request.user)
        if plan is None:
            return Response({"plan": None, "pending": True})
        return Response({"plan": MemberPlanSerializer(plan).data, "pending": False})
