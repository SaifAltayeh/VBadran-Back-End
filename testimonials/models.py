from django.db import models


class Testimonial(models.Model):
    client_name = models.CharField(max_length=120)
    photo = models.TextField(blank=True)
    quote = models.TextField()
    program_name = models.CharField(max_length=160)
    rating = models.PositiveSmallIntegerField(default=5)
    is_featured = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.client_name
