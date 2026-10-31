from datetime import timedelta

from django.utils import timezone

from payments.models import Subscription
from workouts.models import ProgramSchedule, WorkoutCompletion


def subscription_for(user):
    return (
        Subscription.objects.filter(user=user, status=Subscription.Status.ACTIVE)
        .select_related("program")
        .order_by("-start_date")
        .first()
    )


def block_weeks(subscription) -> int:
    return max(1, (subscription.end_date - subscription.start_date).days // 7)


def current_week(subscription) -> int:
    elapsed = (timezone.localdate() - subscription.start_date).days // 7 + 1
    return max(1, min(block_weeks(subscription), elapsed))


def slot_date(subscription, slot: ProgramSchedule):
    return subscription.start_date + timedelta(days=(slot.week_number - 1) * 7 + slot.day_index)


def schedule_status(slot, completed_ids, today) -> str:
    if slot.is_rest:
        return "rest"
    if slot.id in completed_ids:
        return "completed"
    return "upcoming"


def serialize_slot(subscription, slot, completed_ids, today) -> dict:
    workout = slot.workout
    return {
        "id": slot.id,
        "day_label": slot.day_label,
        "date": slot_date(subscription, slot).isoformat(),
        "is_rest": slot.is_rest,
        "status": schedule_status(slot, completed_ids, today),
        "workout": None
        if workout is None
        else {
            "id": workout.id,
            "title": workout.title,
            "slug": workout.slug,
            "duration_minutes": workout.duration_minutes,
            "exercise_count": workout.items.count(),
            "focus": workout.focus,
        },
    }


def week_schedule(subscription, week, completed_ids, today):
    slots = (
        ProgramSchedule.objects.filter(program=subscription.program, week_number=week)
        .select_related("workout")
        .prefetch_related("workout__items")
    )
    return [serialize_slot(subscription, slot, completed_ids, today) for slot in slots]


def next_workout(items):
    today = timezone.localdate().isoformat()
    upcoming = [item for item in items if item["status"] == "upcoming" and item["workout"]]
    for item in upcoming:
        if item["date"] >= today:
            return item
    return upcoming[0] if upcoming else None


def build_dashboard(user) -> dict:
    profile = user.profile
    subscription = subscription_for(user)
    today = timezone.localdate()
    payload = {
        "user": {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": profile.phone,
        },
        "program": None,
        "next_workout": None,
        "week_schedule": [],
        "coach_note": "",
        "progress_summary": progress_summary(user),
        "upcoming_checkin": next_friday(today).isoformat(),
    }
    if subscription is None:
        return payload

    week = current_week(subscription)
    total_weeks = block_weeks(subscription)
    completed_ids = set(
        WorkoutCompletion.objects.filter(user=user, schedule__program=subscription.program).values_list(
            "schedule_id", flat=True
        )
    )
    schedule = week_schedule(subscription, week, completed_ids, today)
    program = subscription.program
    payload.update(
        {
            "program": {
                "title": program.title,
                "slug": program.slug,
                "start_date": subscription.start_date.isoformat(),
                "end_date": subscription.end_date.isoformat(),
                "duration_weeks": total_weeks,
                "current_week": week,
                "goal": program.goal,
                "progress_percent": round((week / total_weeks) * 100),
                "coach_instructions": program.support_overview,
                "nutrition_included": program.includes_nutrition,
                "image": program.featured_image,
            },
            "next_workout": next_workout(schedule),
            "week_schedule": schedule,
            "coach_note": subscription.coach_note,
        }
    )
    return payload


def build_my_program(user) -> dict:
    dashboard = build_dashboard(user)
    subscription = subscription_for(user)
    if subscription is None:
        return {"program": None, "schedule": []}
    return {
        "program": dashboard["program"],
        "coach_note": dashboard["coach_note"],
        "schedule": dashboard["week_schedule"],
        "description": subscription.program.description,
        "training_structure": subscription.program.training_structure,
        "nutrition_overview": subscription.program.nutrition_overview,
    }


def progress_summary(user) -> dict:
    entries = list(user.progress_entries.all())
    latest = entries[-1] if entries else None
    first = entries[0] if entries else None
    change = None
    if latest and first and latest.weight is not None and first.weight is not None and latest.id != first.id:
        change = float(latest.weight - first.weight)
    completed = user.completions.count()
    today = timezone.localdate()
    subscription = subscription_for(user)
    possible = 0
    done = 0
    if subscription:
        done_ids = set(user.completions.values_list("schedule_id", flat=True))
        for slot in subscription.program.schedule.filter(is_rest=False):
            if slot_date(subscription, slot) <= today:
                possible += 1
                if slot.id in done_ids:
                    done += 1
    consistency = round((done / possible) * 100) if possible else 0
    return {
        "weight": float(latest.weight) if latest and latest.weight is not None else None,
        "change": change,
        "workouts_completed": completed,
        "consistency": consistency,
        "latest_date": latest.date.isoformat() if latest else None,
    }


def next_friday(today):
    days = (4 - today.weekday()) % 7
    return today + timedelta(days=days or 7)
