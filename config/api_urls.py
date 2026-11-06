from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import (
    AccountView,
    EmailTokenObtainPairView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
)
from dashboard.views import DashboardView, MyProgramView
from inquiries.views import ContactCreateView
from payments.views import CheckoutView, OrderListView
from programs.views import GymViewSet, PackageViewSet, ProgramViewSet
from testimonials.views import TestimonialViewSet
from transformations.views import TransformationViewSet
from workouts.portal_views import MyPlanView, MyPortalVideosView
from workouts.views import ExerciseViewSet, WorkoutViewSet
from cms.views import SiteHomeView
from config.retired import RetiredMemberServiceView

router = DefaultRouter()
router.register("programs", ProgramViewSet, basename="program")
router.register("packages", PackageViewSet, basename="package")
router.register("gyms", GymViewSet, basename="gym")
router.register("testimonials", TestimonialViewSet, basename="testimonial")
router.register("transformations", TransformationViewSet, basename="transformation")
router.register("exercises", ExerciseViewSet, basename="exercise")
router.register("workouts", WorkoutViewSet, basename="workout")

urlpatterns = [
    path("auth/login/", EmailTokenObtainPairView.as_view(), name="auth-login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/password-reset/", PasswordResetRequestView.as_view(), name="auth-password-reset"),
    path("auth/password-reset/confirm/", PasswordResetConfirmView.as_view(), name="auth-password-confirm"),
    path("account/", AccountView.as_view(), name="account"),
    path("account/password/", PasswordChangeView.as_view(), name="account-password"),
    path("contact/", ContactCreateView.as_view(), name="contact"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("my-program/", MyProgramView.as_view(), name="my-program"),
    path("my-videos/", MyPortalVideosView.as_view(), name="my-videos"),
    path("my-plan/", MyPlanView.as_view(), name="my-plan"),
    path("nutrition/", RetiredMemberServiceView.as_view(), name="nutrition"),
    path("orders/", OrderListView.as_view(), name="orders"),
    path("payments/checkout/", CheckoutView.as_view(), name="checkout"),
    path("messages/", RetiredMemberServiceView.as_view(), name="messages"),
    path("progress/", RetiredMemberServiceView.as_view(), name="progress-list"),
    path("progress/<pk>/", RetiredMemberServiceView.as_view(), name="progress-detail"),
    path("progress-photos/", RetiredMemberServiceView.as_view(), name="progress-photos-list"),
    path("progress-photos/<pk>/", RetiredMemberServiceView.as_view(), name="progress-photos-detail"),
    path("admin/", include("staff.urls")),
    path("site/", SiteHomeView.as_view(), name="site-home"),
    path("", include(router.urls)),
]
