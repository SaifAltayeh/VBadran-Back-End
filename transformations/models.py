from django.db import models

from programs.models import Program


class Transformation(models.Model):
    client_name = models.CharField(max_length=120)
    client_name_ar = models.CharField(max_length=120, blank=True)
    slug = models.SlugField(unique=True)
    before_image = models.TextField()
    after_image = models.TextField()
    cover_image = models.TextField(blank=True)
    image_alt = models.CharField(max_length=255, blank=True)
    duration_weeks = models.PositiveIntegerField(null=True, blank=True)
    result_summary = models.CharField(max_length=200, blank=True)
    result_summary_ar = models.CharField(max_length=200, blank=True)
    program = models.ForeignKey(Program, null=True, blank=True, on_delete=models.SET_NULL)
    program_name = models.CharField(max_length=160, blank=True)
    program_name_ar = models.CharField(max_length=160, blank=True)
    story = models.TextField(blank=True)
    story_ar = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.client_name
