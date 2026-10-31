from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cms.views import SiteHomeAdminView

from .views import (
    ClientAdminViewSet,
    InquiryAdminViewSet,
    OverviewView,
    PackageAdminViewSet,
    ProgramAdminViewSet,
    TestimonialAdminViewSet,
    TransformationAdminViewSet,
)

router = DefaultRouter()
router.register("programs", ProgramAdminViewSet, basename="staff-program")
router.register("packages", PackageAdminViewSet, basename="staff-package")
router.register("transformations", TransformationAdminViewSet, basename="staff-transformation")
router.register("testimonials", TestimonialAdminViewSet, basename="staff-testimonial")
router.register("inquiries", InquiryAdminViewSet, basename="staff-inquiry")
router.register("clients", ClientAdminViewSet, basename="staff-client")

urlpatterns = [
    path("overview/", OverviewView.as_view(), name="staff-overview"),
    path("site/", SiteHomeAdminView.as_view(), name="staff-site"),
    path("", include(router.urls)),
]
