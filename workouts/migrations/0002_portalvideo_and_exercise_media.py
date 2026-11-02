from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("programs", "0002_alter_program_featured_image"),
        ("workouts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="exercise",
            name="thumbnail",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="exercise",
            name="video_url",
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.CreateModel(
            name="PortalVideo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=160)),
                ("description", models.TextField(blank=True)),
                ("video_url", models.CharField(max_length=500)),
                ("thumbnail", models.TextField(blank=True)),
                ("order", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="portal_videos",
                        to="programs.program",
                    ),
                ),
            ],
            options={
                "ordering": ["order", "id"],
            },
        ),
    ]
