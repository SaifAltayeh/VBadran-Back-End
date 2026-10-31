from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Transformation
from .serializers import TransformationSerializer


class TransformationViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = TransformationSerializer
    lookup_field = "slug"
    queryset = Transformation.objects.all()
