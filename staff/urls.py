from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cms.views import MediaUploadView, SiteHomeAdminView, VideoUploadView

from .views import (
    ClientAdminViewSet,
    ExerciseAdminViewSet,
    InquiryAdminViewSet,
    NutritionPlanAdminViewSet,
    OverviewView,
    PackageAdminViewSet,
    PortalVideoAdminViewSet,
    ProgramAdminViewSet,
    ScheduleAdminViewSet,
    SubscriptionAdminViewSet,
    TestimonialAdminViewSet,
    TransformationAdminViewSet,
    WorkoutAdminViewSet,
)

router = DefaultRouter()
router.register("programs", ProgramAdminViewSet, basename="staff-program")
router.register("packages", PackageAdminViewSet, basename="staff-package")
router.register("transformations", TransformationAdminViewSet, basename="staff-transformation")
router.register("testimonials", TestimonialAdminViewSet, basename="staff-testimonial")
router.register("inquiries", InquiryAdminViewSet, basename="staff-inquiry")
router.register("clients", ClientAdminViewSet, basename="staff-client")
router.register("exercises", ExerciseAdminViewSet, basename="staff-exercise")
router.register("portal-videos", PortalVideoAdminViewSet, basename="staff-portal-video")
router.register("workouts", WorkoutAdminViewSet, basename="staff-workout")
router.register("schedules", ScheduleAdminViewSet, basename="staff-schedule")
router.register("nutrition-plans", NutritionPlanAdminViewSet, basename="staff-nutrition-plan")
router.register("subscriptions", SubscriptionAdminViewSet, basename="staff-subscription")

urlpatterns = [
    path("overview/", OverviewView.as_view(), name="staff-overview"),
    path("site/", SiteHomeAdminView.as_view(), name="staff-site"),
    path("uploads/", MediaUploadView.as_view(), name="staff-uploads"),
    path("uploads/video/", VideoUploadView.as_view(), name="staff-video-uploads"),
    path("", include(router.urls)),
]
