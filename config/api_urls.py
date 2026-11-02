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
from messaging.views import MessageThreadView
from nutrition.views import MyNutritionView
from payments.views import CheckoutView, OrderListView
from programs.views import PackageViewSet, ProgramViewSet
from progress.views import ProgressEntryViewSet, ProgressPhotoViewSet
from testimonials.views import TestimonialViewSet
from transformations.views import TransformationViewSet
from workouts.portal_views import MyPortalVideosView
from workouts.views import ExerciseViewSet, WorkoutViewSet
from cms.views import SiteHomeView

router = DefaultRouter()
router.register("programs", ProgramViewSet, basename="program")
router.register("packages", PackageViewSet, basename="package")
router.register("testimonials", TestimonialViewSet, basename="testimonial")
router.register("transformations", TransformationViewSet, basename="transformation")
router.register("exercises", ExerciseViewSet, basename="exercise")
router.register("workouts", WorkoutViewSet, basename="workout")
router.register("progress", ProgressEntryViewSet, basename="progress")
router.register("progress-photos", ProgressPhotoViewSet, basename="progress-photo")

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
    path("nutrition/", MyNutritionView.as_view(), name="nutrition"),
    path("orders/", OrderListView.as_view(), name="orders"),
    path("payments/checkout/", CheckoutView.as_view(), name="checkout"),
    path("messages/", MessageThreadView.as_view(), name="messages"),
    path("admin/", include("staff.urls")),
    path("site/", SiteHomeView.as_view(), name="site-home"),
    path("", include(router.urls)),
]
