from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.views import APIView


class RetiredMemberServiceView(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        raise NotFound("This service is no longer available.")


class RetiredStaffServiceView(RetiredMemberServiceView):
    permission_classes = [IsAdminUser]
