from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("programs", "0003_bilingual_gyms_member_plans"),
        ("workouts", "0004_bilingual_gyms_member_plans"),
    ]

    operations = [
        migrations.AddField(
            model_name="exercise",
            name="packages",
            field=models.ManyToManyField(blank=True, related_name="exercises", to="programs.package"),
        ),
    ]
