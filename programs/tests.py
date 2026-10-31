from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from payments.models import Order
from programs.models import Program


class PlatformApiTests(APITestCase):
    def setUp(self):
        self.program = Program.objects.create(
            title="Online Coaching",
            slug="online-coaching",
            short_description="Remote coaching.",
            description="A full plan.",
            price=Decimal("340.00"),
            duration_weeks=12,
            difficulty="all",
            category="online-coaching",
            goal="Consistency",
            is_active=True,
        )

    def test_programs_are_public(self):
        response = self.client.get("/api/programs/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["slug"], "online-coaching")

    def test_program_detail_by_slug(self):
        response = self.client.get("/api/programs/online-coaching/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Online Coaching")

    def test_dashboard_requires_auth(self):
        response = self.client.get("/api/dashboard/")
        self.assertEqual(response.status_code, 401)

    def test_contact_creates_inquiry(self):
        response = self.client.post(
            "/api/contact/",
            {"name": "Lina", "email": "lina@example.com", "message": "I want online coaching.", "goal": "Strength"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)

    def test_checkout_creates_pending_order(self):
        response = self.client.post(
            "/api/payments/checkout/",
            {
                "full_name": "Lina M",
                "email": "lina@example.com",
                "phone": "000",
                "country": "Jordan",
                "slug": "online-coaching",
                "kind": "program",
                "terms_accepted": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "pending")
        order = Order.objects.get(order_number=response.data["order_number"])
        self.assertIsNone(order.user)
        User = get_user_model()
        self.assertFalse(User.objects.filter(email="lina@example.com").exists())

    def test_login_and_dashboard(self):
        User = get_user_model()
        User.objects.create_user(email="client@example.com", password="Vbadran2026!", first_name="Omar")
        login = self.client.post("/api/auth/login/", {"email": "client@example.com", "password": "Vbadran2026!"}, format="json")
        self.assertEqual(login.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        dashboard = self.client.get("/api/dashboard/")
        self.assertEqual(dashboard.status_code, 200)
        self.assertIsNone(dashboard.data["program"])
