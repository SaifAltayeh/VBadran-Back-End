from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from accounts.models import User
from inquiries.models import ContactInquiry
from payments.models import Order
from programs.models import Package, Program
from testimonials.models import Testimonial
from transformations.models import Transformation

from .serializers import (
    ClientAdminSerializer,
    InquiryAdminSerializer,
    PackageAdminSerializer,
    ProgramAdminSerializer,
    TestimonialAdminSerializer,
    TransformationAdminSerializer,
)


class OverviewView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response(
            {
                "programs": Program.objects.count(),
                "packages": Package.objects.count(),
                "transformations": Transformation.objects.count(),
                "testimonials": Testimonial.objects.count(),
                "inquiries": ContactInquiry.objects.count(),
                "inquiries_new": ContactInquiry.objects.filter(status=ContactInquiry.Status.NEW).count(),
                "clients": User.objects.filter(is_staff=False).count(),
                "orders": Order.objects.count(),
            }
        )


class ProgramAdminViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = ProgramAdminSerializer
    queryset = Program.objects.all()


class PackageAdminViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = PackageAdminSerializer
    queryset = Package.objects.all().select_related("program")


class TransformationAdminViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = TransformationAdminSerializer
    queryset = Transformation.objects.all().select_related("program")


class TestimonialAdminViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = TestimonialAdminSerializer
    queryset = Testimonial.objects.all()


class InquiryAdminViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = InquiryAdminSerializer
    queryset = ContactInquiry.objects.all()
    http_method_names = ["get", "head", "patch", "options"]


class ClientAdminViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = ClientAdminSerializer
    queryset = User.objects.select_related("profile").order_by("-date_joined")
