from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.viewsets import ModelViewSet

from .models import ProgressEntry, ProgressPhoto
from .serializers import ProgressEntrySerializer, ProgressPhotoSerializer


class ProgressEntryViewSet(ModelViewSet):
    serializer_class = ProgressEntrySerializer
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        return ProgressEntry.objects.filter(user=self.request.user)


class ProgressPhotoViewSet(ModelViewSet):
    serializer_class = ProgressPhotoSerializer
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        return ProgressPhoto.objects.filter(user=self.request.user)
