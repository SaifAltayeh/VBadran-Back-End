from datetime import timedelta

from django.utils import timezone

from payments.models import Subscription
from workouts.models import MemberPlan, ProgramSchedule, WorkoutCompletion
from workouts.serializers import MemberPlanSerializer, WorkoutSerializer


def subscription_for(user):
    today = timezone.localdate()
    return (
        Subscription.objects.filter(
            user=user,
            status=Subscription.Status.ACTIVE,
            start_date__lte=today,
            end_date__gte=today,
        )
        .select_related("program", "package", "package__gym", "gym")
        .order_by("-start_date")
        .first()
    )


def active_plan_for(user):
    if subscription_for(user) is None:
        return None
    return (
        MemberPlan.objects.filter(user=user, is_active=True)
        .select_related("workout")
        .prefetch_related("workout__items__exercise")
        .first()
    )


def block_weeks(subscription) -> int:
    return max(1, (subscription.end_date - subscription.start_date).days // 7)


def current_week(subscription) -> int:
    elapsed = (timezone.localdate() - subscription.start_date).days // 7 + 1
    return max(1, min(block_weeks(subscription), elapsed))


def serialize_gym(gym):
    if gym is None:
        return None
    return {"id": gym.id, "name": gym.name, "name_ar": gym.name_ar, "slug": gym.slug}


def serialize_package(package):
    if package is None:
        return None
    return {
        "id": package.id,
        "name": package.name,
        "name_ar": package.name_ar,
        "slug": package.slug,
        "image": package.image,
        "duration_weeks": package.duration_weeks,
        "gym": serialize_gym(package.gym),
    }


def build_dashboard(user) -> dict:
    profile = getattr(user, "profile", None)
    subscription = subscription_for(user)
    plan = active_plan_for(user)
    gym = (subscription.gym if subscription else None) or (getattr(profile, "gym", None) if profile else None)
    package = subscription.package if subscription else None
    payload = {
        "user": {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": getattr(profile, "phone", ""),
            "goal": getattr(profile, "goal", ""),
        },
        "package": serialize_package(package),
        "gym": serialize_gym(gym),
        "goal": getattr(profile, "goal", "") or (order_goal(subscription) if subscription else ""),
        "membership": None,
        "assigned_plan": MemberPlanSerializer(plan).data if plan else None,
        "plan_pending": plan is None,
        "program": None,
        "next_workout": None,
        "week_schedule": [],
        "coach_note": "",
        "progress_summary": {
            "weight": None,
            "change": None,
            "workouts_completed": user.completions.count(),
            "consistency": 0,
            "latest_date": None,
        },
        "upcoming_checkin": None,
    }
    if subscription is None:
        return payload

    start = subscription.start_date
    end = subscription.end_date
    payload["membership"] = {
        "status": subscription.status,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "duration_weeks": block_weeks(subscription),
    }
    if subscription.program_id:
        program = subscription.program
        payload["program"] = {
            "title": program.title,
            "title_ar": program.title_ar,
            "slug": program.slug,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "duration_weeks": program.duration_weeks or block_weeks(subscription),
            "current_week": current_week(subscription),
            "goal": program.goal,
            "progress_percent": 0,
            "coach_instructions": program.support_overview,
            "nutrition_included": False,
            "image": program.featured_image,
        }
    return payload


def order_goal(subscription):
    if subscription.order_id:
        return subscription.order.goal
    return ""


def build_my_program(user) -> dict:
    dashboard = build_dashboard(user)
    plan = active_plan_for(user)
    return {
        "program": dashboard["program"],
        "package": dashboard["package"],
        "gym": dashboard["gym"],
        "goal": dashboard["goal"],
        "plan": dashboard["assigned_plan"],
        "plan_pending": dashboard["plan_pending"],
        "workout": WorkoutSerializer(plan.workout).data if plan else None,
        "coach_note": "",
        "schedule": [],
        "description": "",
        "training_structure": plan.workout.description if plan else "",
        "nutrition_overview": "",
    }
