from rest_framework.response import Response
from rest_framework.views import APIView

from .services import build_dashboard, build_my_program


class DashboardView(APIView):
    def get(self, request):
        return Response(build_dashboard(request.user))


class MyProgramView(APIView):
    def get(self, request):
        return Response(build_my_program(request.user))
