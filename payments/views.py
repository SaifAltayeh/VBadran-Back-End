from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from programs.models import Package, Program

from .models import Order
from .services import create_pending_order


class OrderListView(APIView):
    def get(self, request):
        orders = Order.objects.filter(user=request.user).select_related("program", "package")
        return Response([serialize_order(order) for order in orders])


class CheckoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        if not data.get("terms_accepted"):
            return Response({"detail": "Accept the terms to continue."}, status=status.HTTP_400_BAD_REQUEST)
        required = ["full_name", "email", "slug", "kind"]
        missing = [field for field in required if not data.get(field)]
        if missing:
            return Response({"detail": "Check the required fields."}, status=status.HTTP_400_BAD_REQUEST)

        program = None
        package = None
        kind = data.get("kind")
        slug = data.get("slug")
        if kind == "package":
            package = Package.objects.filter(slug=slug, is_active=True).first()
        elif kind == "program":
            program = Program.objects.filter(slug=slug, is_active=True).first()
        else:
            return Response({"detail": "Unknown product."}, status=status.HTTP_400_BAD_REQUEST)
        if program is None and package is None:
            return Response({"detail": "That program is not available."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user if request.user.is_authenticated else None
        order = create_pending_order(
            full_name=data.get("full_name", "").strip(),
            email=data.get("email", "").strip(),
            phone=data.get("phone", ""),
            country=data.get("country", ""),
            program=program,
            package=package,
            terms_accepted=True,
            user=user,
        )
        payload = serialize_order(order)
        payload["payment"] = {
            "provider": "unconfigured",
            "status": "pending",
            "detail": "No card was charged. Connect a payment provider to capture payment and open access.",
        }
        return Response(payload, status=status.HTTP_201_CREATED)


def serialize_order(order: Order) -> dict:
    if order.program_id:
        title = order.program.title
    elif order.package_id:
        title = order.package.name
    else:
        title = order.items.first().title if order.items.exists() else "Program"
    return {
        "order_number": order.order_number,
        "title": title,
        "email": order.email,
        "full_name": order.full_name,
        "amount": str(order.amount),
        "currency": order.currency,
        "status": order.status,
        "created_at": order.created_at.date().isoformat(),
    }
