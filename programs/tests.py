from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from payments.models import Order, Subscription
from programs.models import Gym, Package, Program
from progress.models import ProgressEntry
from workouts.models import Exercise, MemberPlan, PortalVideo, Workout, WorkoutExercise


class PlatformApiTests(APITestCase):
    def setUp(self):
        self.gym, _ = Gym.objects.get_or_create(
            slug="spark",
            defaults={"name": "Spark", "name_ar": "سبارك", "is_active": True, "order": 1},
        )
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
        self.package = Package.objects.create(
            name="Spark",
            slug="spark",
            price=Decimal("30.000"),
            currency="KWD",
            gym=self.gym,
            is_active=True,
        )
        self.inactive = Package.objects.create(
            name="Elite",
            slug="elite",
            price=Decimal("90.000"),
            currency="KWD",
            gym=self.gym,
            is_active=False,
        )

    def test_programs_are_public(self):
        response = self.client.get("/api/programs/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["slug"], "online-coaching")

    def test_program_detail_by_slug(self):
        response = self.client.get("/api/programs/online-coaching/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Online Coaching")

    def test_inactive_package_is_hidden(self):
        response = self.client.get("/api/packages/elite/")
        self.assertEqual(response.status_code, 404)

    def test_dashboard_requires_auth(self):
        response = self.client.get("/api/dashboard/")
        self.assertEqual(response.status_code, 401)

    def test_contact_creates_inquiry(self):
        response = self.client.post(
            "/api/contact/",
            {"name": "Lina", "email": "lina@example.com", "message": "I want a training package.", "goal": "Strength"},
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
                "country": "Kuwait",
                "slug": "spark",
                "kind": "package",
                "goal": "strength",
                "gym_id": self.gym.id,
                "terms_accepted": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "pending")
        self.assertEqual(response.data["payment"]["provider"], "pending-upay")
        order = Order.objects.get(order_number=response.data["order_number"])
        self.assertIsNone(order.user)
        User = get_user_model()
        self.assertFalse(User.objects.filter(email="lina@example.com").exists())

    def test_checkout_rejects_inactive_package(self):
        response = self.client.post(
            "/api/payments/checkout/",
            {
                "full_name": "Lina M",
                "email": "lina@example.com",
                "slug": "elite",
                "kind": "package",
                "goal": "strength",
                "gym_id": self.gym.id,
                "terms_accepted": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 404)

    def test_login_and_dashboard(self):
        User = get_user_model()
        User.objects.create_user(email="client@example.com", password="Vbadran2026!", first_name="Omar")
        login = self.client.post("/api/auth/login/", {"email": "client@example.com", "password": "Vbadran2026!"}, format="json")
        self.assertEqual(login.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        dashboard = self.client.get("/api/dashboard/")
        self.assertEqual(dashboard.status_code, 200)
        self.assertIsNone(dashboard.data["program"])
        self.assertTrue(dashboard.data["plan_pending"])


class SecurityAndMemberAccessTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.gym, _ = Gym.objects.get_or_create(
            slug="spark",
            defaults={"name": "Spark", "name_ar": "سبارك", "is_active": True, "order": 1},
        )
        self.package = Package.objects.create(
            name="Spark",
            slug="spark-access",
            price=Decimal("30.000"),
            currency="KWD",
            gym=self.gym,
            is_active=True,
        )
        self.other_package = Package.objects.create(
            name="Platinum",
            slug="platinum-access",
            price=Decimal("50.000"),
            currency="KWD",
            gym=self.gym,
            is_active=True,
        )
        self.member = User.objects.create_user(email="member-a@example.com", password="Vbadran2026!", first_name="A")
        self.other = User.objects.create_user(email="member-b@example.com", password="Vbadran2026!", first_name="B")
        self.staff = User.objects.create_user(
            email="staff@example.com",
            password="Vbadran2026!",
            first_name="Coach",
            is_staff=True,
        )
        today = timezone.localdate()
        Subscription.objects.create(
            user=self.member,
            package=self.package,
            gym=self.gym,
            status=Subscription.Status.ACTIVE,
            start_date=today,
            end_date=today + timedelta(weeks=12),
        )
        allowed = PortalVideo.objects.create(title="Spark video", video_url="https://youtu.be/spark", is_active=True)
        allowed.packages.add(self.package)
        denied = PortalVideo.objects.create(title="Platinum video", video_url="https://youtu.be/platinum", is_active=True)
        denied.packages.add(self.other_package)
        spark_exercise = Exercise.objects.create(
            name="Spark video",
            slug="spark-video",
            muscle_group="Spark",
            video_url="https://youtu.be/spark",
        )
        spark_exercise.packages.add(self.package)
        platinum_exercise = Exercise.objects.create(
            name="Platinum video",
            slug="platinum-video",
            muscle_group="Platinum",
            video_url="https://youtu.be/platinum",
        )
        platinum_exercise.packages.add(self.other_package)
        self.workout = Workout.objects.create(title="Push", slug="push", description="Upper body")
        MemberPlan.objects.create(user=self.member, workout=self.workout, is_active=True)
        ProgressEntry.objects.create(user=self.member, date=today, weight=80, notes="private")

    def auth(self, user):
        login = self.client.post("/api/auth/login/", {"email": user.email, "password": "Vbadran2026!"}, format="json")
        self.assertEqual(login.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        return login.data

    def test_register_saves_gym_and_goal(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "new-member@example.com",
                "password": "Vbadran2026!",
                "first_name": "Nour",
                "goal": "fat-loss",
                "gym_id": self.gym.id,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["goal"], "fat-loss")
        self.assertEqual(response.data["gym"]["slug"], "spark")

    def test_admin_endpoints_require_staff(self):
        unauth = self.client.get("/api/admin/packages/")
        self.assertEqual(unauth.status_code, 401)
        self.auth(self.member)
        forbidden = self.client.get("/api/admin/packages/")
        self.assertEqual(forbidden.status_code, 403)
        site = self.client.patch("/api/admin/site/", {"site": {"arabicOnly": True}}, format="json")
        self.assertEqual(site.status_code, 403)
        upload = self.client.post("/api/admin/uploads/video/")
        self.assertEqual(upload.status_code, 403)

    def test_staff_can_assign_plan_and_member_sees_it(self):
        self.auth(self.staff)
        assigned = self.client.get(f"/api/admin/member-plans/?user={self.other.id}")
        self.assertEqual(assigned.status_code, 200)
        create = self.client.post(
            "/api/admin/member-plans/",
            {"user": self.other.id, "workout": self.workout.id, "notes": "Start here", "is_active": True},
            format="json",
        )
        self.assertEqual(create.status_code, 201)
        self.auth(self.other)
        hidden = self.client.get("/api/my-plan/")
        self.assertEqual(hidden.status_code, 200)
        self.assertTrue(hidden.data["pending"])
        self.assertIsNone(hidden.data["plan"])
        today = timezone.localdate()
        Subscription.objects.create(
            user=self.other,
            package=self.package,
            gym=self.gym,
            status=Subscription.Status.ACTIVE,
            start_date=today,
            end_date=today + timedelta(weeks=12),
        )
        visible = self.client.get("/api/my-plan/")
        self.assertEqual(visible.status_code, 200)
        self.assertFalse(visible.data["pending"])
        self.assertEqual(visible.data["plan"]["workout"]["slug"], "push")

    def test_assigned_plan_requires_valid_membership(self):
        User = get_user_model()
        today = timezone.localdate()
        expired = User.objects.create_user(email="expired@example.com", password="Vbadran2026!", first_name="E")
        Subscription.objects.create(
            user=expired,
            package=self.package,
            gym=self.gym,
            status=Subscription.Status.ACTIVE,
            start_date=today - timedelta(weeks=20),
            end_date=today - timedelta(days=1),
        )
        MemberPlan.objects.create(user=expired, workout=self.workout, is_active=True)
        MemberPlan.objects.create(user=self.other, workout=self.workout, is_active=True)

        self.auth(self.other)
        none = self.client.get("/api/my-plan/")
        self.assertTrue(none.data["pending"])
        self.assertIsNone(none.data["plan"])
        self.assertEqual(self.client.get("/api/workouts/").data, [])
        dashboard = self.client.get("/api/dashboard/")
        self.assertIsNone(dashboard.data["assigned_plan"])

        self.auth(expired)
        expired_plan = self.client.get("/api/my-plan/")
        self.assertTrue(expired_plan.data["pending"])
        self.assertIsNone(expired_plan.data["plan"])
        self.assertEqual(self.client.get("/api/exercises/").data, [])

        self.auth(self.member)
        valid = self.client.get("/api/my-plan/")
        self.assertFalse(valid.data["pending"])
        self.assertEqual(valid.data["plan"]["workout"]["slug"], "push")

    def test_member_cannot_read_another_member_progress(self):
        private_id = ProgressEntry.objects.get(user=self.member).id
        self.auth(self.other)
        dashboard = self.client.get("/api/dashboard/")
        self.assertEqual(dashboard.data["user"]["email"], "member-b@example.com")
        listing = self.client.get("/api/progress/")
        self.assertEqual(listing.status_code, 404)
        detail = self.client.get(f"/api/progress/{private_id}/")
        self.assertEqual(detail.status_code, 404)
        self.assertTrue(ProgressEntry.objects.filter(pk=private_id).exists())

    def test_unauthorized_videos_are_hidden(self):
        blocked = self.client.get("/api/my-videos/")
        self.assertEqual(blocked.status_code, 401)
        self.auth(self.other)
        empty = self.client.get("/api/my-videos/")
        self.assertEqual(empty.status_code, 200)
        self.assertEqual(empty.data["videos"], [])
        self.auth(self.member)
        allowed = self.client.get("/api/my-videos/")
        titles = [item["title"] for item in allowed.data["videos"]]
        self.assertEqual(titles, ["Spark video"])

    def test_package_exercises_are_scoped(self):
        blocked = self.client.get("/api/exercises/")
        self.assertEqual(blocked.status_code, 401)
        self.auth(self.other)
        empty = self.client.get("/api/exercises/")
        self.assertEqual(empty.status_code, 200)
        self.assertEqual(empty.data, [])
        self.auth(self.member)
        allowed = self.client.get("/api/exercises/")
        names = [item["name"] for item in allowed.data]
        self.assertEqual(names, ["Spark video"])

    def test_staff_can_delete_exercise_used_in_workout(self):
        exercise = Exercise.objects.create(
            name="Temp delete",
            slug="temp-delete",
            muscle_group="Test",
            video_url="https://youtu.be/temp-delete",
        )
        WorkoutExercise.objects.create(workout=self.workout, exercise=exercise, sets="3", reps="8")
        self.auth(self.staff)
        response = self.client.delete(f"/api/admin/exercises/{exercise.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Exercise.objects.filter(pk=exercise.id).exists())
        self.assertFalse(WorkoutExercise.objects.filter(exercise_id=exercise.id).exists())

    def test_shared_videos_use_member_package_cover(self):
        shared = Exercise.objects.create(
            name="All gyms 1",
            slug="all-gyms-1",
            muscle_group="All gyms",
            video_url="https://youtu.be/shared",
        )
        shared.packages.add(self.package, self.other_package)
        self.auth(self.member)
        payload = {item["slug"]: item for item in self.client.get("/api/exercises/").data}
        self.assertEqual(payload["all-gyms-1"]["thumbnail"], "/images/packages/spark-cover.jpg")
        self.assertEqual(payload["spark-video"]["thumbnail"], "")

    def test_checkout_does_not_create_subscription(self):
        User = get_user_model()
        before = Subscription.objects.count()
        response = self.client.post(
            "/api/payments/checkout/",
            {
                "full_name": "No Access",
                "email": "no-access@example.com",
                "slug": "spark-access",
                "kind": "package",
                "goal": "strength",
                "gym_id": self.gym.id,
                "terms_accepted": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "pending")
        self.assertEqual(Subscription.objects.count(), before)
        self.assertFalse(User.objects.filter(email="no-access@example.com").exists())

    def test_site_exposes_arabic_only_and_legal_fields(self):
        response = self.client.get("/api/site/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("arabicOnly", response.data["site"])
        self.assertIn("terms", response.data["pages"])
        self.assertIn("privacy", response.data["pages"])

    def test_staff_can_remove_footer_socials_and_phone(self):
        self.auth(self.staff)
        current = self.client.get("/api/admin/site/")
        self.assertEqual(current.status_code, 200)
        site = dict(current.data["site"])
        site["phoneDisplay"] = ""
        site["phoneHref"] = ""
        site["socials"] = []
        saved = self.client.patch("/api/admin/site/", {"site": site}, format="json")
        self.assertEqual(saved.status_code, 200, saved.data)
        self.assertEqual(saved.data["site"]["phoneDisplay"], "")
        self.assertEqual(saved.data["site"]["socials"], [])
        public = self.client.get("/api/site/")
        self.assertEqual(public.data["site"]["phoneDisplay"], "")
        self.assertEqual(public.data["site"]["socials"], [])


class GymPackageCatalogTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.staff = User.objects.create_user(
            email="staff-catalog@example.com",
            password="local-test-pass",
            is_staff=True,
        )
        self.gyms = {}
        for slug, name, name_ar, order in (
            ("spark", "Spark", "سبارك", 0),
            ("platinum", "Platinum", "بلاتينوم", 1),
            ("oxygen", "Oxygen", "أوكسجين", 2),
        ):
            gym, _ = Gym.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "name_ar": name_ar, "is_active": True, "order": order},
            )
            self.gyms[slug] = gym

    def test_staff_can_create_gym_packages_and_attach_hosted_videos(self):
        login = self.client.post(
            "/api/auth/login/",
            {"email": self.staff.email, "password": "local-test-pass"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        created = []
        for slug in ("spark", "platinum", "oxygen"):
            gym = self.gyms[slug]
            response = self.client.post(
                "/api/admin/packages/",
                {
                    "name": gym.name,
                    "name_ar": gym.name_ar,
                    "slug": slug,
                    "price": "0.000",
                    "currency": "KWD",
                    "gym": gym.id,
                    "image": "/images/packages/placeholder.jpg",
                    "training_plan": True,
                    "nutrition": False,
                    "weekly_checkins": False,
                    "video_library": True,
                    "coach_support": False,
                    "progress_tracking": False,
                    "program_adjustments": False,
                    "messaging": False,
                    "is_active": False,
                },
                format="json",
            )
            self.assertEqual(response.status_code, 201, response.data)
            self.assertEqual(response.data["gym"], gym.id)
            self.assertEqual(response.data["name_ar"], gym.name_ar)
            self.assertTrue(response.data["video_library"])
            self.assertFalse(response.data["is_active"])
            created.append(response.data)

        video = self.client.post(
            "/api/admin/portal-videos/",
            {
                "title": "Spark movement",
                "title_ar": "حركة سبارك",
                "video_url": "https://www.youtube.com/watch?v=testvideo",
                "package_ids": [created[0]["id"]],
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(video.status_code, 201, video.data)
        self.assertEqual(video.data["package_ids"], [created[0]["id"]])
        self.assertEqual(video.data["video_url"], "https://www.youtube.com/watch?v=testvideo")

        blocked = self.client.post(
            "/api/admin/portal-videos/",
            {
                "title": "Data URL is not storage",
                "video_url": "data:video/mp4;base64,AAAA",
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(blocked.status_code, 400)


class DemoSeedGuardTests(APITestCase):
    def test_seed_demo_blocked_without_debug(self):
        from django.core.management import call_command
        from django.core.management.base import CommandError
        from django.test import override_settings

        with override_settings(DEBUG=False, ALLOW_DEMO_SEED=True, ON_VERCEL=False, DEMO_PASSWORD="x"):
            with self.assertRaisesMessage(CommandError, "local development only"):
                call_command("seed_demo")

    def test_seed_demo_blocked_without_allow_flag(self):
        from django.core.management import call_command
        from django.core.management.base import CommandError
        from django.test import override_settings

        with override_settings(DEBUG=True, ALLOW_DEMO_SEED=False, ON_VERCEL=False, DEMO_PASSWORD="x"):
            with self.assertRaisesMessage(CommandError, "ALLOW_DEMO_SEED"):
                call_command("seed_demo")

    def test_seed_demo_blocked_on_vercel(self):
        from django.core.management import call_command
        from django.core.management.base import CommandError
        from django.test import override_settings

        with override_settings(DEBUG=True, ALLOW_DEMO_SEED=True, ON_VERCEL=True, DEMO_PASSWORD="x"):
            with self.assertRaisesMessage(CommandError, "Vercel"):
                call_command("seed_demo")


class PublicPackageCatalogTests(APITestCase):
    def test_public_catalog_returns_database_packages_only(self):
        gym, _ = Gym.objects.get_or_create(slug="spark", defaults={"name": "Spark", "name_ar": "سبارك", "is_active": True})
        Package.objects.create(
            name="Spark",
            slug="spark",
            price=Decimal("25.000"),
            currency="KWD",
            gym=gym,
            is_active=True,
        )
        response = self.client.get("/api/packages/")
        self.assertEqual(response.status_code, 200)
        slugs = [item["slug"] for item in response.data]
        self.assertEqual(slugs, ["spark"])
        for demo in ("foundation", "progress", "transform", "elite"):
            self.assertNotIn(demo, slugs)


class LoadGymPackagesTests(APITestCase):
    def test_import_refuses_non_local_hosts(self):
        from django.core.management import call_command
        from django.core.management.base import CommandError
        from django.test import override_settings

        with override_settings(DEBUG=False, ON_VERCEL=False, ALLOW_GYM_PACKAGE_IMPORT=False):
            with self.assertRaisesMessage(CommandError, "local-only"):
                call_command("load_gym_packages")

    def test_repeat_import_does_not_change_client_package_data(self):
        import tempfile
        from pathlib import Path

        from django.core.management import call_command
        from django.test import override_settings

        gym, _ = Gym.objects.get_or_create(
            slug="spark",
            defaults={"name": "Spark", "name_ar": "سبارك", "is_active": True, "order": 0},
        )
        spark = Package.objects.create(
            name="Spark",
            slug="spark",
            price=Decimal("99.500"),
            currency="KWD",
            gym=gym,
            tagline="Client approved tagline",
            description="Client approved description",
            is_active=True,
            image="/images/packages/spark.png",
        )
        elite = Package.objects.create(
            name="Elite",
            slug="elite",
            price=Decimal("10.000"),
            currency="KWD",
            is_active=True,
        )
        extra = Exercise.objects.create(
            name="Keep me",
            slug="keep-me",
            muscle_group="Test",
            video_url="/media/videos/keep-me.MOV",
            is_active=True,
        )
        with tempfile.TemporaryDirectory() as tmp:
            videos = Path(tmp) / "videos"
            videos.mkdir()
            (videos / "spark-1.MOV").write_bytes(b"x")
            with override_settings(DEBUG=True, ON_VERCEL=False, ALLOW_GYM_PACKAGE_IMPORT=True, MEDIA_ROOT=tmp):
                call_command("load_gym_packages")
                call_command("load_gym_packages")
        spark.refresh_from_db()
        elite.refresh_from_db()
        extra.refresh_from_db()
        self.assertEqual(spark.price, Decimal("99.500"))
        self.assertEqual(spark.tagline, "Client approved tagline")
        self.assertEqual(spark.description, "Client approved description")
        self.assertTrue(spark.is_active)
        self.assertTrue(elite.is_active)
        self.assertTrue(extra.is_active)
        self.assertFalse(Package.objects.filter(slug="platinum").exists())
        self.assertEqual(Exercise.objects.filter(slug="spark-1").count(), 1)
        self.assertEqual(list(Exercise.objects.get(slug="spark-1").packages.values_list("slug", flat=True)), ["spark"])

    def test_import_does_not_invent_missing_package_prices(self):
        import tempfile
        from pathlib import Path

        from django.core.management import call_command
        from django.test import override_settings

        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "videos").mkdir()
            with override_settings(DEBUG=True, ON_VERCEL=False, ALLOW_GYM_PACKAGE_IMPORT=True, MEDIA_ROOT=tmp):
                call_command("load_gym_packages")
        self.assertFalse(Package.objects.filter(slug__in=["spark", "platinum", "oxygen"]).exists())


class ObsoleteCoachingServiceTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.member = User.objects.create_user(email="retired-member@example.com", password="Vbadran2026!", first_name="M")
        self.staff = User.objects.create_user(
            email="retired-staff@example.com",
            password="Vbadran2026!",
            first_name="Coach",
            is_staff=True,
        )
        gym, _ = Gym.objects.get_or_create(slug="spark", defaults={"name": "Spark", "name_ar": "سبارك", "is_active": True})
        package = Package.objects.create(
            name="Spark",
            slug="spark-retired",
            price=Decimal("25.000"),
            currency="KWD",
            gym=gym,
            is_active=True,
        )
        today = timezone.localdate()
        Subscription.objects.create(
            user=self.member,
            package=package,
            gym=gym,
            status=Subscription.Status.ACTIVE,
            start_date=today,
            end_date=today + timedelta(weeks=12),
        )
        ProgressEntry.objects.create(user=self.member, date=today, weight=80, notes="keep")

    def auth(self, user):
        login = self.client.post("/api/auth/login/", {"email": user.email, "password": "Vbadran2026!"}, format="json")
        self.assertEqual(login.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

    def test_obsolete_member_services_require_auth_then_404(self):
        for path in ("/api/nutrition/", "/api/messages/", "/api/progress/", "/api/progress-photos/"):
            blocked = self.client.get(path)
            self.assertEqual(blocked.status_code, 401, path)
        self.auth(self.member)
        for path in ("/api/nutrition/", "/api/messages/", "/api/progress/", "/api/progress-photos/"):
            gone = self.client.get(path)
            self.assertEqual(gone.status_code, 404, path)
            self.assertIn("no longer available", gone.data["detail"])
        posted = self.client.post("/api/messages/", {"body": "Hello"}, format="json")
        self.assertEqual(posted.status_code, 404)
        self.assertTrue(ProgressEntry.objects.filter(user=self.member, notes="keep").exists())

    def test_admin_nutrition_is_retired_without_deleting_records(self):
        blocked = self.client.get("/api/admin/nutrition-plans/")
        self.assertEqual(blocked.status_code, 401)
        self.auth(self.staff)
        gone = self.client.get("/api/admin/nutrition-plans/")
        self.assertEqual(gone.status_code, 404)
        created = self.client.post("/api/admin/nutrition-plans/", {"title": "Should not create"}, format="json")
        self.assertEqual(created.status_code, 404)

    def test_active_member_routes_remain_authorized(self):
        blocked = self.client.get("/api/my-plan/")
        self.assertEqual(blocked.status_code, 401)
        blocked_videos = self.client.get("/api/my-videos/")
        self.assertEqual(blocked_videos.status_code, 401)
        blocked_exercises = self.client.get("/api/exercises/")
        self.assertEqual(blocked_exercises.status_code, 401)
        self.auth(self.member)
        plan = self.client.get("/api/my-plan/")
        self.assertEqual(plan.status_code, 200)
        videos = self.client.get("/api/my-videos/")
        self.assertEqual(videos.status_code, 200)
        exercises = self.client.get("/api/exercises/")
        self.assertEqual(exercises.status_code, 200)
