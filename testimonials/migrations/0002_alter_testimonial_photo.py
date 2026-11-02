from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("testimonials", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="testimonial",
            name="photo",
            field=models.TextField(blank=True),
        ),
    ]
