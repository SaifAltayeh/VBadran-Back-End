from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Testimonial
from .serializers import TestimonialSerializer


class TestimonialViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = TestimonialSerializer
    queryset = Testimonial.objects.filter(is_featured=True)
