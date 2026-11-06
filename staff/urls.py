from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cms.views import MediaUploadView, SiteHomeAdminView, VideoUploadView
from config.retired import RetiredStaffServiceView

from .views import (
    ClientAdminViewSet,
    ExerciseAdminViewSet,
    GymAdminViewSet,
    InquiryAdminViewSet,
    MemberPlanAdminViewSet,
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
router.register("gyms", GymAdminViewSet, basename="staff-gym")
router.register("transformations", TransformationAdminViewSet, basename="staff-transformation")
router.register("testimonials", TestimonialAdminViewSet, basename="staff-testimonial")
router.register("inquiries", InquiryAdminViewSet, basename="staff-inquiry")
router.register("clients", ClientAdminViewSet, basename="staff-client")
router.register("exercises", ExerciseAdminViewSet, basename="staff-exercise")
router.register("portal-videos", PortalVideoAdminViewSet, basename="staff-portal-video")
router.register("workouts", WorkoutAdminViewSet, basename="staff-workout")
router.register("schedules", ScheduleAdminViewSet, basename="staff-schedule")
router.register("subscriptions", SubscriptionAdminViewSet, basename="staff-subscription")
router.register("member-plans", MemberPlanAdminViewSet, basename="staff-member-plan")

urlpatterns = [
    path("overview/", OverviewView.as_view(), name="staff-overview"),
    path("site/", SiteHomeAdminView.as_view(), name="staff-site"),
    path("uploads/", MediaUploadView.as_view(), name="staff-uploads"),
    path("uploads/video/", VideoUploadView.as_view(), name="staff-video-uploads"),
    path("nutrition-plans/", RetiredStaffServiceView.as_view(), name="staff-nutrition-plan-list"),
    path("nutrition-plans/<pk>/", RetiredStaffServiceView.as_view(), name="staff-nutrition-plan-detail"),
    path("", include(router.urls)),
]
