from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.services import subscription_for

from .models import PortalVideo
from .serializers import PortalVideoSerializer


class MyPortalVideosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subscription = subscription_for(request.user)
        if subscription is None:
            return Response({"videos": [], "program": None})
        videos = PortalVideo.objects.filter(program=subscription.program, is_active=True)
        return Response(
            {
                "program": {"id": subscription.program_id, "title": subscription.program.title},
                "videos": PortalVideoSerializer(videos, many=True).data,
            }
        )
