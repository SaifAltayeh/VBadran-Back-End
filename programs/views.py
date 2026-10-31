from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Package, Program
from .serializers import PackageSerializer, ProgramSerializer


class ProgramViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = ProgramSerializer
    lookup_field = "slug"
    filterset_fields = ["category", "is_featured"]
    queryset = Program.objects.filter(is_active=True).prefetch_related("features", "faqs")


class PackageViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = PackageSerializer
    lookup_field = "slug"
    queryset = Package.objects.filter(is_active=True).select_related("program")
