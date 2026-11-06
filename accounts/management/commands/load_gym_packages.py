from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from programs.models import Gym, Package
from workouts.models import Exercise, Workout

PPL_AR = """وصف التمارين :
الجدول عباره عن push pull leg
عدد الأيام 5 أيام بالاسبوع ..
السبت : push
الأحد : pull
الاثنين: أوف
الثلاثاء : push تركيز كتف
الأربعاء : pull
الخميس:  leg
الجمعه : أوف

عدد الجولات : 3 جولات
عدد التكرارات : 8-10 عدات فعليه"""

PPL_EN = """Exercise description:
The schedule is push / pull / leg.
Training days: 5 per week.
Saturday: push
Sunday: pull
Monday: off
Tuesday: push, shoulder focus
Wednesday: pull
Thursday: leg
Friday: off

Sets: 3
Reps: 8–10 working reps"""

PACKAGE_VIDEOS = {
    "spark": 5,
    "platinum": 5,
    "oxygen": 5,
}

GYMS = (
    ("spark", "Spark", "سبارك", 0),
    ("platinum", "Platinum", "بلاتينوم", 1),
    ("oxygen", "Oxygen", "أوكسجين", 2),
)

WORKOUT_DEFAULTS = {
    "title": "Push Pull Leg",
    "title_ar": "دفع سحب رجل",
    "description": PPL_EN,
    "description_ar": PPL_AR,
    "focus": "Push / pull / leg",
    "focus_ar": "دفع / سحب / رجل",
    "duration_minutes": 60,
    "coach_notes": "3 sets, 8–10 working reps.",
    "coach_notes_ar": "عدد الجولات : 3 جولات\nعدد التكرارات : 8-10 عدات فعليه",
}


def local_import_allowed():
    if getattr(settings, "ON_VERCEL", False):
        return False
    if settings.DEBUG:
        return True
    return getattr(settings, "ALLOW_GYM_PACKAGE_IMPORT", False)


class Command(BaseCommand):
    help = (
        "Attach local Spark/Platinum/Oxygen images and videos to existing packages. "
        "Never invents or overwrites prices, descriptions, or active states."
    )

    def handle(self, *args, **options):
        if not local_import_allowed():
            raise CommandError(
                "load_gym_packages is local-only. Run it with DEBUG=true, or set "
                "ALLOW_GYM_PACKAGE_IMPORT=true after an explicit review. It never overwrites prices."
            )

        media_videos = Path(settings.MEDIA_ROOT) / "videos"
        if not media_videos.exists():
            raise CommandError(f"Missing video folder: {media_videos}")

        gyms = {}
        packages = {}
        for slug, name, name_ar, order in GYMS:
            gym, _ = Gym.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "name_ar": name_ar, "is_active": True, "order": order},
            )
            gyms[slug] = gym
            package = Package.objects.filter(slug=slug).first()
            if package is None:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping {slug}: create this package in admin with client-approved "
                        "prices and descriptions, then re-run to attach media."
                    )
                )
                continue
            changed_fields = []
            if not package.gym_id:
                package.gym = gym
                changed_fields.append("gym")
            if not package.image:
                package.image = f"/images/packages/{slug}.png"
                changed_fields.append("image")
            if not package.image_alt:
                package.image_alt = name
                changed_fields.append("image_alt")
            if changed_fields:
                package.save(update_fields=changed_fields)
                self.stdout.write(f"Filled blank media fields on {slug}: {', '.join(changed_fields)}")
            else:
                self.stdout.write(f"Left existing {slug} package unchanged")
            packages[slug] = package

        workout, created = Workout.objects.get_or_create(slug="push-pull-leg", defaults=WORKOUT_DEFAULTS)
        if not created:
            fill = []
            for field, value in WORKOUT_DEFAULTS.items():
                if not getattr(workout, field):
                    setattr(workout, field, value)
                    fill.append(field)
            if fill:
                workout.save(update_fields=fill)

        def upsert_exercise(slug, name, name_ar, filename, package_slugs, muscle_group, cover):
            path = media_videos / filename
            if not path.exists():
                self.stdout.write(self.style.WARNING(f"Missing {filename}, skipped"))
                return
            video_url = f"/media/videos/{filename}"
            exercise, created_exercise = Exercise.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "name_ar": name_ar,
                    "description": name,
                    "description_ar": name_ar,
                    "video_url": video_url,
                    "thumbnail": cover,
                    "image_alt": name,
                    "muscle_group": muscle_group,
                    "difficulty": Exercise.Difficulty.INTERMEDIATE,
                    "is_active": True,
                },
            )
            if not created_exercise:
                fill = []
                if not exercise.video_url:
                    exercise.video_url = video_url
                    fill.append("video_url")
                if cover and not exercise.thumbnail:
                    exercise.thumbnail = cover
                    fill.append("thumbnail")
                if fill:
                    exercise.save(update_fields=fill)
            linked = [packages[item] for item in package_slugs if item in packages]
            if linked:
                exercise.packages.add(*linked)
            return exercise

        for slug, count in PACKAGE_VIDEOS.items():
            if slug not in packages:
                continue
            gym = gyms[slug]
            cover = f"/images/packages/{slug}-cover.jpg"
            for index in range(1, count + 1):
                upsert_exercise(
                    f"{slug}-{index}",
                    f"{gym.name} {index}",
                    f"{gym.name_ar} {index}",
                    f"{slug}-{index}.MOV",
                    [slug],
                    gym.name,
                    cover,
                )

        shared_targets = [slug for slug in PACKAGE_VIDEOS if slug in packages]
        if shared_targets:
            for index in (1, 2):
                upsert_exercise(
                    f"all-gyms-{index}",
                    f"All gyms {index}",
                    f"لجميع الصالات {index}",
                    f"shared-{index}.MOV",
                    shared_targets,
                    "All gyms",
                    "",
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Gym media import finished. Workout id={workout.id} slug={workout.slug}. "
                "Existing package prices, descriptions, and active states were not changed."
            )
        )
