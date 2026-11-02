from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("programs", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="program",
            name="featured_image",
            field=models.TextField(blank=True),
        ),
    ]
