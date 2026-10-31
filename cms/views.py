from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .defaults import DEFAULT_HOME
from .models import SiteHome


def deep_merge(base, incoming):
    if not isinstance(base, dict) or not isinstance(incoming, dict):
        return incoming
    merged = dict(base)
    for key, value in incoming.items():
        merged[key] = deep_merge(base.get(key), value) if key in base else value
    return merged


class SiteHomeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(deep_merge(DEFAULT_HOME, SiteHome.load().data or {}))


class SiteHomeAdminView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response(deep_merge(DEFAULT_HOME, SiteHome.load().data or {}))

    def patch(self, request):
        page = SiteHome.load()
        payload = request.data.get("data", request.data)
        page.data = deep_merge(deep_merge(DEFAULT_HOME, page.data or {}), payload)
        page.save(update_fields=["data"])
        return Response(page.data)
