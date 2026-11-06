from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from programs.models import Gym, Package, Program

from .models import Order
from .services import create_pending_order

PAYMENT_PENDING_DETAIL = (
    "UPAY / KNET INTEGRATION: NOT IMPLEMENTED — PENDING API DOCUMENTATION. "
    "This request only stored a pending order. No payment was taken and membership was not activated."
)


class OrderListView(APIView):
    def get(self, request):
        orders = Order.objects.filter(user=request.user).select_related("program", "package", "gym")
        return Response([serialize_order(order) for order in orders])


class CheckoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        if not data.get("terms_accepted"):
            return Response({"detail": "Accept the terms to continue."}, status=status.HTTP_400_BAD_REQUEST)
        required = ["full_name", "email", "slug", "kind", "goal"]
        missing = [field for field in required if not str(data.get(field) or "").strip()]
        if missing:
            return Response({"detail": "Check the required fields."}, status=status.HTTP_400_BAD_REQUEST)

        program = None
        package = None
        kind = data.get("kind")
        slug = data.get("slug")
        if kind == "package":
            package = Package.objects.filter(slug=slug, is_active=True).select_related("gym", "program").first()
        elif kind == "program":
            program = Program.objects.filter(slug=slug, is_active=True).first()
        else:
            return Response({"detail": "Unknown product."}, status=status.HTTP_400_BAD_REQUEST)
        if program is None and package is None:
            return Response({"detail": "That package is not available."}, status=status.HTTP_404_NOT_FOUND)

        gym = None
        if package and package.gym_id:
            gym = package.gym
        else:
            gym_id = data.get("gym_id") or data.get("gym")
            if gym_id:
                gym = Gym.objects.filter(pk=gym_id, is_active=True).first()
            elif data.get("gym_slug"):
                gym = Gym.objects.filter(slug=data.get("gym_slug"), is_active=True).first()
        if gym is None:
            return Response({"detail": "Choose a gym."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user if request.user.is_authenticated else None
        order = create_pending_order(
            full_name=data.get("full_name", "").strip(),
            email=data.get("email", "").strip(),
            phone=data.get("phone", ""),
            country=data.get("country", ""),
            goal=str(data.get("goal") or "").strip(),
            gym=gym,
            program=program,
            package=package,
            terms_accepted=True,
            user=user,
        )
        payload = serialize_order(order)
        payload["payment"] = {
            "provider": "pending-upay",
            "status": "pending",
            "detail": PAYMENT_PENDING_DETAIL,
        }
        return Response(payload, status=status.HTTP_201_CREATED)


def serialize_order(order: Order) -> dict:
    if order.program_id:
        title = order.program.title
    elif order.package_id:
        title = order.package.name
    else:
        title = order.items.first().title if order.items.exists() else "Package"
    return {
        "order_number": order.order_number,
        "title": title,
        "email": order.email,
        "full_name": order.full_name,
        "amount": str(order.amount),
        "currency": order.currency,
        "status": order.status,
        "goal": order.goal,
        "gym": None
        if not order.gym_id
        else {"id": order.gym_id, "name": order.gym.name, "name_ar": order.gym.name_ar, "slug": order.gym.slug},
        "created_at": order.created_at.date().isoformat(),
    }
