from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from accounts.models import User
from messaging.models import Conversation, Message
from nutrition.models import Meal, NutritionDay, NutritionNote, NutritionPlan
from payments.models import Order, Subscription
from payments.services import make_order_number
from programs.models import Package, Program, ProgramFAQ, ProgramFeature
from progress.models import ProgressEntry
from testimonials.models import Testimonial
from transformations.models import Transformation
from workouts.models import Exercise, ProgramSchedule, Workout, WorkoutCompletion, WorkoutExercise


PROGRAMS = [
    {
        "title": "Personal Training",
        "slug": "personal-training",
        "short_description": "In-person coaching programmed around your schedule, movement, and goals.",
        "description": "Sessions happen with the coach in the room. The plan is written for your week, then adjusted from what you actually lift, how you recover, and what the calendar allows.",
        "price": "480.00",
        "duration_weeks": 12,
        "difficulty": "all",
        "category": "personal-training",
        "goal": "Strength and consistency, coached in person",
        "featured_image": "/images/programs/stage-pose.jpg",
        "image_alt": "Badran on stage, hands on hips, during a physique competition",
        "is_featured": False,
        "includes_nutrition": False,
        "includes_training": True,
        "expected_outcome": "A repeatable training week, better lifts, and a plan you can keep after the block.",
        "who_for": "You want a coach present for the sessions, not only a plan in an app.",
        "training_structure": "Three or four coached sessions each week. Strength work comes first.",
        "nutrition_overview": "Training is the focus. Nutrition can be added in a combined package.",
        "support_overview": "You train with the coach. Between sessions you have the written plan.",
        "features": ["In-person coached sessions", "Custom weekly training plan", "Technique review in the room", "Progress check every two weeks"],
        "faqs": [("Where do sessions happen?", "At the coach’s training base. Hours are set when you start.")],
    },
    {
        "title": "Online Coaching",
        "slug": "online-coaching",
        "short_description": "A full plan, weekly check-ins, and adjustments wherever you train.",
        "description": "You train where you are. Each week you get the sessions, the intent behind them, and a check-in that changes the next week.",
        "price": "340.00",
        "duration_weeks": 12,
        "difficulty": "all",
        "category": "online-coaching",
        "goal": "Consistent training with remote coach support",
        "featured_image": "/images/hero/coach-studio.jpg",
        "image_alt": "Badran in a white training shirt, studio portrait",
        "is_featured": False,
        "includes_nutrition": True,
        "includes_training": True,
        "expected_outcome": "A plan you can run without a coach in the room.",
        "who_for": "You have a place to train and want programming plus accountability.",
        "training_structure": "Four training days and planned rest.",
        "nutrition_overview": "Daily targets for calories and protein, adjusted from your check-in.",
        "support_overview": "Weekly written check-in and direct messages.",
        "features": ["Custom training plan", "Weekly check-ins", "Video exercise library", "Nutrition targets", "Direct coach messages"],
        "faqs": [("Do I need a full gym?", "A rack, a bench, and dumbbells cover most of the plan.")],
    },
    {
        "title": "Body Transformation",
        "slug": "body-transformation",
        "short_description": "Twelve weeks for body composition, strength, and a routine that lasts.",
        "description": "A single block with a clear target. Training and nutrition sit in one plan. The point is a physique and a schedule you can still run when the twelve weeks end.",
        "price": "520.00",
        "duration_weeks": 12,
        "difficulty": "intermediate",
        "category": "body-transformation",
        "goal": "Change body composition without losing strength",
        "featured_image": "/images/programs/trophy.jpg",
        "image_alt": "Badran on stage holding a first-place medal",
        "is_featured": True,
        "includes_nutrition": True,
        "includes_training": True,
        "expected_outcome": "A leaner, stronger frame and a week of training and food you understand.",
        "who_for": "You have trained before and can commit to twelve weeks.",
        "training_structure": "Four lifting days with a clear progression.",
        "nutrition_overview": "Calories, protein, and a meal structure for training and rest days.",
        "support_overview": "Train the sessions as written. Send the Friday check-in with weight and a short note. If a joint feels sharp, stop that exercise and message the same day.",
        "features": ["12-week training block", "Nutrition targets and meal structure", "Weekly check-ins", "Progress tracking", "Direct messages"],
        "faqs": [("Is this a crash plan?", "No. If a deficit is used, it is sized so training quality stays high.")],
    },
    {
        "title": "Training Programs",
        "slug": "training-programs",
        "short_description": "Structured sessions with progression, written so you can follow them precisely.",
        "description": "The programming without the full coaching layer. You get the block, the sessions, and the video references.",
        "price": "190.00",
        "duration_weeks": 8,
        "difficulty": "intermediate",
        "category": "training-plans",
        "goal": "Follow a structured strength block",
        "featured_image": "/images/programs/stage-clasp.jpg",
        "image_alt": "Badran on stage in a front pose with hands clasped",
        "is_featured": False,
        "includes_nutrition": False,
        "includes_training": True,
        "expected_outcome": "Eight weeks of sessions you can execute without inventing the workout.",
        "who_for": "You like to train on your own and want the sets and progression decided.",
        "training_structure": "Four days each week. The same patterns repeat.",
        "nutrition_overview": "Not included.",
        "support_overview": "The plan and the video library.",
        "features": ["8-week session plan", "Progression built into the weeks", "Video exercise library"],
        "faqs": [("Can I ask questions?", "Coach notes are on each session. Ongoing messaging is in the coaching packages.")],
    },
    {
        "title": "Nutrition Guidance",
        "slug": "nutrition-guidance",
        "short_description": "Targets and meal structure that fit the way you actually eat.",
        "description": "You get daily targets, a way to build meals, and adjustments when the week changes.",
        "price": "160.00",
        "duration_weeks": 8,
        "difficulty": "all",
        "category": "nutrition",
        "goal": "Eat in a way that supports training",
        "featured_image": "/images/about/back-gym.jpg",
        "image_alt": "Badran from behind in the gym",
        "is_featured": False,
        "includes_nutrition": True,
        "includes_training": False,
        "expected_outcome": "Clear daily targets and a meal pattern you can shop for.",
        "who_for": "Your training is already in place, or you want to fix food first.",
        "training_structure": "Training is not rewritten here.",
        "nutrition_overview": "Calories, protein, carbohydrates, fats, and meal examples.",
        "support_overview": "A check-in every two weeks.",
        "features": ["Calorie and macro targets", "Training-day and rest-day structure", "Meal examples"],
        "faqs": [("Do I have to weigh every meal?", "No. Targets come with a simple way to hit them.")],
    },
    {
        "title": "Training + Nutrition",
        "slug": "training-nutrition",
        "short_description": "Sessions, food, and weekly accountability in one system.",
        "description": "Training is progressed. Food is specific. The weekly check-in ties the two together.",
        "price": "640.00",
        "duration_weeks": 12,
        "difficulty": "all",
        "category": "training-nutrition",
        "goal": "Train and eat from one plan",
        "featured_image": "/images/programs/stage-front.jpg",
        "image_alt": "Badran walking on stage in competition shape",
        "is_featured": False,
        "includes_nutrition": True,
        "includes_training": True,
        "expected_outcome": "Strength moving in the right direction and a nutrition rhythm that matches training.",
        "who_for": "You want one coach owning both sides.",
        "training_structure": "Four lifting days and planned rest.",
        "nutrition_overview": "Full targets and a weekly adjustment.",
        "support_overview": "Weekly check-in, direct messages, and priority replies.",
        "features": ["Custom training and nutrition", "Weekly check-ins", "Progress tracking", "Priority coach messages"],
        "faqs": [("How is this different from Online Coaching?", "This is the fuller version: priority replies and a longer weekly review.")],
    },
    {
        "title": "Custom Sports Programs",
        "slug": "custom-sports",
        "short_description": "Strength that transfers, written around practice and competition.",
        "description": "For athletes who already have a sport to play. The lifting supports the season.",
        "price": "560.00",
        "duration_weeks": 12,
        "difficulty": "advanced",
        "category": "custom-sports",
        "goal": "Get stronger without stealing from your sport",
        "featured_image": "/images/programs/winners.jpg",
        "image_alt": "Two athletes on stage with medals",
        "is_featured": False,
        "includes_nutrition": True,
        "includes_training": True,
        "expected_outcome": "Stronger main lifts and a weekly plan that respects the competitive calendar.",
        "who_for": "Athletes who need strength work that fits practice and games.",
        "training_structure": "Two to four lifting days depending on the season.",
        "nutrition_overview": "Fueling for training and competition days.",
        "support_overview": "Direct messages and a weekly look at upcoming fixtures.",
        "features": ["Season-aware programming", "Strength and power sessions", "Competition-week adjustments", "Coach messaging"],
        "faqs": [("Which sports?", "Field, court, and combat sports. The assessment covers your calendar.")],
    },
]


class Command(BaseCommand):
    help = "Load local demo catalog and test accounts. Never run this on staging or production."

    def handle(self, *args, **options):
        if getattr(settings, "ON_VERCEL", False):
            raise CommandError("seed_demo cannot run on Vercel or hosted production.")
        if not settings.DEBUG:
            raise CommandError("seed_demo is local development only.")
        if not getattr(settings, "ALLOW_DEMO_SEED", False):
            raise CommandError("Refusing to seed. Set ALLOW_DEMO_SEED=true in local .env.")
        password = (getattr(settings, "DEMO_PASSWORD", "") or "").strip()
        if not password:
            raise CommandError("Set DEMO_PASSWORD in local .env. Do not commit it.")
        programs = {}
        for data in PROGRAMS:
            features = data.pop("features")
            faqs = data.pop("faqs")
            program, _ = Program.objects.update_or_create(slug=data["slug"], defaults=data)
            program.features.all().delete()
            program.faqs.all().delete()
            for index, text in enumerate(features):
                ProgramFeature.objects.create(program=program, text=text, order=index)
            for index, (question, answer) in enumerate(faqs):
                ProgramFAQ.objects.create(program=program, question=question, answer=answer, order=index)
            programs[program.slug] = program
            data["features"] = features
            data["faqs"] = faqs

        # DEMO catalog only. Client gym packages (Spark, Platinum, Oxygen) are CMS-managed
        # and must not be created or priced here.
        package_rows = [
            ("Foundation", "foundation", "The plan, clearly written.", "An eight-week training block with the video library.", 8, "190.00", "Eight weeks of sessions you can run on your own.", False, "training-programs", "Plan access", False, False, False),
            ("Progress", "progress", "Training, food, and a weekly check-in.", "Online coaching for twelve weeks.", 12, "340.00", "A steadier week and visible progress by the end of the block.", False, "online-coaching", "Weekly check-in", True, True, True),
            ("Transform", "transform", "The full twelve-week block.", "Body composition, strength, nutrition, and coach review.", 12, "520.00", "A leaner, stronger twelve weeks, with a routine you can continue.", True, "body-transformation", "Weekly coach review", True, True, True),
            ("Elite", "elite", "Priority access for sixteen weeks.", "Training and nutrition with faster replies.", 16, "780.00", "Sixteen weeks of priority coaching.", False, "training-nutrition", "Priority access", True, True, True),
        ]
        for index, row in enumerate(package_rows):
            name, slug, tagline, description, weeks, price, outcome, highlighted, program_slug, support, nutrition, checkins, messaging = row
            Package.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "tagline": tagline,
                    "description": description,
                    "duration_weeks": weeks,
                    "price": Decimal(price),
                    "expected_outcome": outcome,
                    "is_highlighted": highlighted,
                    "program": programs[program_slug],
                    "support_label": support,
                    "training_plan": True,
                    "nutrition": nutrition,
                    "weekly_checkins": checkins,
                    "video_library": True,
                    "coach_support": checkins,
                    "progress_tracking": True,
                    "program_adjustments": checkins,
                    "messaging": messaging,
                    "order": index,
                    "is_active": True,
                },
            )

        exercise_rows = [
            ("Back Squat", "back-squat", "Quads", "/images/programs/stage-clasp.jpg", "Brace, sit between the hips, stand tall."),
            ("Romanian Deadlift", "romanian-deadlift", "Hamstrings", "/images/programs/stage-side.jpg", "Push the hips back and keep the bar close."),
            ("Bench Press", "bench-press", "Chest", "/images/programs/stage-front.jpg", "Lower to the lower chest and press up."),
            ("Bent-Over Row", "bent-over-row", "Back", "/images/programs/stage-pose.jpg", "Pull to the lower ribs without losing the brace."),
            ("Walking Lunge", "walking-lunge", "Legs", "/images/about/gym-walk.jpg", "Step long enough that the back knee travels down."),
            ("Overhead Press", "overhead-press", "Shoulders", "/images/programs/trophy.jpg", "Ribs down, bar to lockout over the mid-foot."),
            ("Pull-Up", "pull-up", "Back", "/images/programs/stage-back.jpg", "Pull the chest toward the bar."),
            ("Plank", "plank", "Core", "/images/about/back-gym.jpg", "Hold a straight line and keep breathing."),
        ]
        exercises = {}
        for name, slug, muscle, image, instructions in exercise_rows:
            exercise, _ = Exercise.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "description": instructions,
                    "thumbnail": image,
                    "image_alt": name,
                    "muscle_group": muscle,
                    "difficulty": "beginner" if slug == "plank" else "intermediate",
                    "instructions": instructions,
                    "tips": "Stop if a joint feels sharp.",
                },
            )
            exercises[slug] = exercise

        workout_defs = [
            ("Lower Strength", "lower-strength", 55, "Lower body", "5 minutes easy, then two light squat sets.", "Leave one rep in reserve.", [("back-squat", "4", "5", 150), ("romanian-deadlift", "3", "8", 120), ("walking-lunge", "3", "10 / leg", 75), ("plank", "3", "30 sec", 45)]),
            ("Upper Strength", "upper-strength", 50, "Upper body", "Band pull-aparts, then two easy press sets.", "Smooth reps. No bounce.", [("bench-press", "4", "6", 150), ("bent-over-row", "4", "8", 120), ("overhead-press", "3", "8", 90), ("pull-up", "3", "6-8", 90)]),
            ("Full Body", "full-body", 45, "Full body", "Two minutes easy, then the first exercise light.", "Finish on time.", [("back-squat", "3", "5", 120), ("bench-press", "3", "8", 90), ("bent-over-row", "3", "10", 75), ("plank", "2", "30 sec", 30)]),
            ("Conditioning", "conditioning", 35, "Conditioning", "Easy pace for four minutes.", "You should still speak a short sentence.", [("walking-lunge", "6", "40 m", 60), ("plank", "3", "20 sec", 40)]),
        ]
        workouts = {}
        for title, slug, minutes, focus, warmup, notes, items in workout_defs:
            workout, _ = Workout.objects.update_or_create(
                slug=slug,
                defaults={"title": title, "duration_minutes": minutes, "focus": focus, "warmup": warmup, "coach_notes": notes, "description": title},
            )
            workout.items.all().delete()
            for index, (exercise_slug, sets, reps, rest) in enumerate(items):
                WorkoutExercise.objects.create(
                    workout=workout,
                    exercise=exercises[exercise_slug],
                    sets=sets,
                    reps=reps,
                    rest_seconds=rest,
                    tempo="2-0-1-0",
                    order=index,
                )
            workouts[slug] = workout

        featured = programs["body-transformation"]
        featured.schedule.all().delete()
        pattern = [
            (0, "Monday", "lower-strength", False),
            (1, "Tuesday", "upper-strength", False),
            (2, "Wednesday", None, True),
            (3, "Thursday", "full-body", False),
            (4, "Friday", "conditioning", False),
            (5, "Saturday", None, True),
            (6, "Sunday", None, True),
        ]
        for week in range(1, 13):
            for day_index, label, workout_slug, is_rest in pattern:
                ProgramSchedule.objects.create(
                    program=featured,
                    workout=None if is_rest else workouts[workout_slug],
                    week_number=week,
                    day_index=day_index,
                    day_label=label,
                    is_rest=is_rest,
                )

        for slug in ("body-transformation", "online-coaching", "nutrition-guidance", "training-nutrition", "custom-sports"):
            program = programs[slug]
            plan, _ = NutritionPlan.objects.update_or_create(
                program=program,
                defaults={
                    "title": f"{program.title} targets",
                    "overview": "These numbers are a starting point. They move after the check-in.",
                    "calories": 2400,
                    "protein_g": 180,
                    "carbs_g": 230,
                    "fats_g": 70,
                    "coach_notes": "Hit protein first. Place most of the carbohydrates around training.",
                    "download_label": "Current targets",
                },
            )
            plan.days.all().delete()
            plan.notes.all().delete()
            training = NutritionDay.objects.create(plan=plan, name="Training day", order=0)
            rest = NutritionDay.objects.create(plan=plan, name="Rest day", order=1)
            Meal.objects.create(day=training, name="Breakfast", suggestion="Eggs, fruit, and oats or bread.", order=0)
            Meal.objects.create(day=training, name="Lunch", suggestion="Rice, chicken or fish, and vegetables.", order=1)
            Meal.objects.create(day=training, name="Dinner", suggestion="Potatoes or rice, protein, olive oil, salad.", order=2)
            Meal.objects.create(day=rest, name="Breakfast", suggestion="Same protein, slightly less starch.", order=0)
            Meal.objects.create(day=rest, name="Dinner", suggestion="The training dinner with one less handful of starch.", order=1)
            NutritionNote.objects.create(plan=plan, body="If weight drops faster than planned, add food.", order=0)

        quotes = [
            ("Lina M.", "The plan fit my work weeks. I stopped guessing in the gym and started finishing the sessions that were written.", "Online Coaching"),
            ("Omar H.", "Check-ins were direct. When my schedule changed, the training changed with it.", "Body Transformation"),
            ("Sara K.", "I came in inconsistent. Twelve weeks later I had a routine I could keep.", "Training + Nutrition"),
            ("Yusuf A.", "Clear sessions, clear targets, and someone who actually looked at the week.", "Personal Training"),
        ]
        Testimonial.objects.all().delete()
        for index, (name, quote, program_name) in enumerate(quotes):
            Testimonial.objects.create(client_name=name, quote=quote, program_name=program_name, rating=5, order=index)

        stories = [
            ("adam", "Adam", 12, "Leaner midsection. More shape through the chest and arms.", "Online Coaching", "client-1", "Adam trained at home and in a gym. Twelve weeks, same structure, loads that moved."),
            ("sami", "Sami", 16, "Stronger upper body. A week he could actually repeat.", "Body Transformation", "client-2", "The first month was about showing up. By week sixteen the weeks had stopped resetting."),
            ("hadi", "Hadi", 10, "Tighter waist. Training that survived a busy month.", "Training + Nutrition", "client-3", "Food and sessions were written together. The plan got shorter when work got louder."),
            ("rami", "Rami", 12, "More muscle through the shoulders. A cleaner routine.", "Online Coaching", "client-4", "Twelve weeks of the online block. The photos are the record of the weeks underneath."),
        ]
        for index, (slug, name, weeks, summary, program_name, image, story) in enumerate(stories):
            path = f"/images/transformations/{image}.jpg"
            Transformation.objects.update_or_create(
                slug=slug,
                defaults={
                    "client_name": name,
                    "before_image": path,
                    "after_image": path,
                    "cover_image": path,
                    "image_alt": f"Online coaching progress photos for {name}",
                    "duration_weeks": weeks,
                    "result_summary": summary,
                    "program_name": program_name,
                    "program": programs.get("online-coaching"),
                    "story": story,
                    "is_featured": index < 2,
                    "order": index,
                },
            )

        def user_for(email, first, last, staff=False, superuser=False):
            user, _ = User.objects.get_or_create(email=email)
            user.first_name = first
            user.last_name = last
            user.is_staff = staff
            user.is_superuser = superuser
            user.set_password(password)
            user.save()
            return user

        admin = user_for("admin@vbadran.com", "VBADRAN", "Admin", True, True)
        coach = user_for("coach@vbadran.com", "Badran", "Coach")
        client = user_for("client@vbadran.com", "Omar", "Hassan")
        client.profile.phone = "+962 79 000 0000"
        client.profile.country = "Jordan"
        client.profile.goal = "Change body composition without losing strength"
        client.profile.fitness_level = "intermediate"
        client.profile.save()

        today = timezone.localdate()
        monday = today - timedelta(days=today.weekday())
        start = monday - timedelta(weeks=4)
        order, _ = Order.objects.update_or_create(
            email=client.email,
            program=featured,
            defaults={
                "user": client,
                "order_number": Order.objects.filter(email=client.email, program=featured).values_list("order_number", flat=True).first() or make_order_number(),
                "full_name": "Omar Hassan",
                "phone": client.profile.phone,
                "country": "Jordan",
                "package": Package.objects.get(slug="transform"),
                "amount": Decimal("520.00"),
                "status": Order.Status.PAID,
                "terms_accepted": True,
            },
        )
        Subscription.objects.update_or_create(
            user=client,
            program=featured,
            defaults={
                "order": order,
                "status": Subscription.Status.ACTIVE,
                "start_date": start,
                "end_date": start + timedelta(weeks=12),
                "coach_note": "Week 5 stays on the same lifts. Add a little load on the squat only if Monday moved well.",
            },
        )
        subscription = Subscription.objects.get(user=client, program=featured)
        WorkoutCompletion.objects.filter(user=client).delete()
        for slot in featured.schedule.all():
            slot_day = subscription.start_date + timedelta(days=(slot.week_number - 1) * 7 + slot.day_index)
            if not slot.is_rest and slot_day < today:
                WorkoutCompletion.objects.create(user=client, schedule=slot)

        ProgressEntry.objects.filter(user=client).delete()
        weights = [Decimal("86.4"), Decimal("85.6"), Decimal("84.8"), Decimal("83.9"), Decimal("83.1")]
        for index, weight in enumerate(weights):
            ProgressEntry.objects.create(
                user=client,
                date=start + timedelta(weeks=index),
                weight=weight,
                waist=Decimal("92") - Decimal(index) * Decimal("0.8"),
                chest=Decimal("102"),
                arms=Decimal("36"),
                legs=Decimal("60"),
                notes="Week 5. Strength is holding." if index == len(weights) - 1 else "",
            )

        conversation, _ = Conversation.objects.get_or_create(client=client, defaults={"subject": "Coach messages"})
        conversation.messages.all().delete()
        Message.objects.create(conversation=conversation, sender=coach, is_coach=True, body="Week 5 is lower body on Monday. If the knee feels sharp on the lunge, stop that exercise and tell me.")
        Message.objects.create(conversation=conversation, sender=client, is_coach=False, body="Knee was fine. Energy is better when I train in the afternoon.")
        Message.objects.create(conversation=conversation, sender=coach, is_coach=True, body="Good. Hold the calories where they are. Protein stays the priority on training days.")

        self.stdout.write(self.style.SUCCESS("Local demo content ready."))
        self.stdout.write("Demo emails: admin@vbadran.com, client@vbadran.com, coach@vbadran.com")
        self.stdout.write("Passwords come from DEMO_PASSWORD in local .env. Do not use this command on staging.")
        self.stdout.write(f"Unused account handle kept for admin id {admin.id}.")
