from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("workouts", "0002_portalvideo_and_exercise_media"),
    ]

    operations = [
        migrations.AlterField(
            model_name="exercise",
            name="video_url",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="portalvideo",
            name="video_url",
            field=models.TextField(),
        ),
    ]
