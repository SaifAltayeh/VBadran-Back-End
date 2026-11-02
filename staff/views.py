from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from accounts.models import User
from inquiries.models import ContactInquiry
from nutrition.models import NutritionPlan
from payments.models import Order, Subscription
from programs.models import Package, Program
from testimonials.models import Testimonial
from transformations.models import Transformation
from workouts.models import Exercise, PortalVideo, ProgramSchedule, Workout

from .serializers import (
    ClientAdminSerializer,
    ExerciseAdminSerializer,
    InquiryAdminSerializer,
    NutritionPlanAdminSerializer,
    PackageAdminSerializer,
    PortalVideoAdminSerializer,
    ProgramAdminSerializer,
    ScheduleAdminSerializer,
    SubscriptionAdminSerializer,
    TestimonialAdminSerializer,
    TransformationAdminSerializer,
    WorkoutAdminSerializer,
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
                "exercises": Exercise.objects.count(),
                "workouts": Workout.objects.count(),
                "portal_videos": PortalVideo.objects.count(),
                "subscriptions_active": Subscription.objects.filter(status=Subscription.Status.ACTIVE).count(),
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


class ExerciseAdminViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = ExerciseAdminSerializer
    queryset = Exercise.objects.all()


class PortalVideoAdminViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = PortalVideoAdminSerializer
    queryset = PortalVideo.objects.select_related("program").all()
    filterset_fields = ["program", "is_active"]


class WorkoutAdminViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = WorkoutAdminSerializer
    queryset = Workout.objects.prefetch_related("items__exercise").all()


class ScheduleAdminViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = ScheduleAdminSerializer
    queryset = ProgramSchedule.objects.select_related("program", "workout").all()
    filterset_fields = ["program", "week_number"]


class NutritionPlanAdminViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = NutritionPlanAdminSerializer
    queryset = NutritionPlan.objects.select_related("program").prefetch_related("days__meals", "notes").all()


class SubscriptionAdminViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = SubscriptionAdminSerializer
    queryset = Subscription.objects.select_related("user", "program").all()
    filterset_fields = ["status", "program", "user"]
