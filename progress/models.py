from django.conf import settings
from django.db import models


class ProgressEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="progress_entries", on_delete=models.CASCADE)
    date = models.DateField()
    weight = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    body_fat = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    chest = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    waist = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    arms = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    legs = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["date"]
        unique_together = ("user", "date")

    def __str__(self):
        return f"{self.user.email} · {self.date}"


class ProgressPhoto(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="progress_photos", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="progress/")
    caption = models.CharField(max_length=160, blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user.email} · {self.date}"
