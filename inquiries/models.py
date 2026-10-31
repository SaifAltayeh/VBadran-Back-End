from django.db import models


class ContactInquiry(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        READ = "read", "Read"
        CLOSED = "closed", "Closed"

    name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=32, blank=True)
    goal = models.CharField(max_length=255, blank=True)
    fitness_level = models.CharField(max_length=32, blank=True)
    program = models.CharField(max_length=160, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "contact inquiry"
        verbose_name_plural = "contact inquiries"

    def __str__(self):
        return f"{self.name} · {self.email}"
