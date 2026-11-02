from django.db import models

from programs.models import Program


class Transformation(models.Model):
    client_name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    before_image = models.TextField()
    after_image = models.TextField()
    cover_image = models.TextField(blank=True)
    image_alt = models.CharField(max_length=255, blank=True)
    duration_weeks = models.PositiveIntegerField()
    result_summary = models.CharField(max_length=200)
    program = models.ForeignKey(Program, null=True, blank=True, on_delete=models.SET_NULL)
    program_name = models.CharField(max_length=160)
    story = models.TextField()
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.client_name
