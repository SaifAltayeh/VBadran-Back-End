from django.db import migrations
from django.utils.text import slugify


def move_portal_videos(apps, schema_editor):
    Exercise = apps.get_model("workouts", "Exercise")
    PortalVideo = apps.get_model("workouts", "PortalVideo")
    Gym = apps.get_model("programs", "Gym")

    used_slugs = set(Exercise.objects.values_list("slug", flat=True))
    url_map = {item.video_url: item for item in Exercise.objects.exclude(video_url="") if item.video_url}

    for video in PortalVideo.objects.all().prefetch_related("packages"):
        exercise = url_map.get(video.video_url)
        if exercise is None:
            base = slugify(video.title) or f"video-{video.pk}"
            slug = base
            index = 2
            while slug in used_slugs:
                slug = f"{base}-{index}"
                index += 1
            used_slugs.add(slug)
            muscle = "Training"
            if video.gym_id:
                gym = Gym.objects.filter(pk=video.gym_id).first()
                if gym:
                    muscle = gym.name
            exercise = Exercise.objects.create(
                name=video.title,
                name_ar=video.title_ar,
                slug=slug,
                description=video.description,
                description_ar=video.description_ar,
                video_url=video.video_url,
                thumbnail=video.thumbnail,
                muscle_group=muscle,
                difficulty="intermediate",
                is_active=video.is_active,
            )
            if video.video_url:
                url_map[video.video_url] = exercise
        elif video.is_active and not exercise.is_active:
            exercise.is_active = True
            exercise.save(update_fields=["is_active"])

        package_ids = list(video.packages.values_list("id", flat=True))
        if package_ids:
            exercise.packages.add(*package_ids)
        if video.is_active:
            video.is_active = False
            video.save(update_fields=["is_active"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("workouts", "0005_exercise_packages"),
    ]

    operations = [
        migrations.RunPython(move_portal_videos, noop),
    ]
