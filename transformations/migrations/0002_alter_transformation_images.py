from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("transformations", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transformation",
            name="before_image",
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="transformation",
            name="after_image",
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name="transformation",
            name="cover_image",
            field=models.TextField(blank=True),
        ),
    ]
