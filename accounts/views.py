from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from config.throttles import AuthThrottle
from payments.models import Order, Subscription

from .models import User
from .serializers import (
    AccountSerializer,
    EmailTokenObtainPairSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    RegisterSerializer,
)


class EmailTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = EmailTokenObtainPairSerializer
    throttle_classes = [AuthThrottle]


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(AccountSerializer(user).data, status=status.HTTP_201_CREATED)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]

    def post(self, request):
        email = (request.data.get("email") or "").strip()
        user = User.objects.filter(email__iexact=email).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            link = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"
            send_mail(
                subject="Reset your Badran password",
                message=f"Use this link to choose a new password:\n\n{link}\n\nIf you did not ask for this, you can ignore the email.",
                from_email=None,
                recipient_list=[user.email],
                fail_silently=True,
            )
        return Response({"detail": "If an account exists for that email, a reset link has been sent."})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            uid = force_str(urlsafe_base64_decode(serializer.validated_data["uid"]))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({"detail": "This reset link is invalid or has expired."}, status=400)
        if not default_token_generator.check_token(user, serializer.validated_data["token"]):
            return Response({"detail": "This reset link is invalid or has expired."}, status=400)
        user.set_password(serializer.validated_data["password"])
        user.save(update_fields=["password"])
        return Response({"detail": "Password updated. You can sign in."})


class AccountView(APIView):
    def get(self, request):
        purchases = []
        subscription = (
            Subscription.objects.filter(user=request.user)
            .select_related("program", "package")
            .order_by("-start_date")
            .first()
        )
        for order in Order.objects.filter(user=request.user).select_related("program", "package")[:12]:
            if order.package_id:
                title = order.package.name
                title_ar = order.package.name_ar
            elif order.program_id:
                title = order.program.title
                title_ar = order.program.title_ar
            else:
                title = "Program"
                title_ar = "برنامج"
            purchases.append(
                {
                    "order_number": order.order_number,
                    "title": title,
                    "title_ar": title_ar,
                    "status": order.status,
                    "amount": str(order.amount),
                    "currency": order.currency,
                    "created_at": order.created_at.date().isoformat(),
                }
            )
        data = AccountSerializer(request.user).data
        if subscription and subscription.package_id:
            data["current_program"] = subscription.package.name
            data["current_program_ar"] = subscription.package.name_ar
        elif subscription and subscription.program_id:
            data["current_program"] = subscription.program.title
            data["current_program_ar"] = subscription.program.title_ar
        else:
            data["current_program"] = None
            data["current_program_ar"] = None
        data["purchases"] = purchases
        return Response(data)

    def patch(self, request):
        serializer = AccountSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(AccountSerializer(request.user).data)


class PasswordChangeView(APIView):
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        return Response({"detail": "Password updated."})
