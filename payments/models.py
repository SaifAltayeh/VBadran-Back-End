from django.conf import settings
from django.db import models

from programs.models import Package, Program


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"
        EXPIRED = "expired", "Expired"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="orders",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    order_number = models.CharField(max_length=24, unique=True)
    full_name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=32, blank=True)
    country = models.CharField(max_length=80, blank=True)
    program = models.ForeignKey(Program, related_name="orders", null=True, blank=True, on_delete=models.SET_NULL)
    package = models.ForeignKey(Package, related_name="orders", null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=8, default="USD")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    terms_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    title = models.CharField(max_length=180)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title


class Subscription(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        CANCELLED = "cancelled", "Cancelled"
        EXPIRED = "expired", "Expired"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="subscriptions", on_delete=models.CASCADE)
    program = models.ForeignKey(Program, related_name="subscriptions", on_delete=models.PROTECT)
    order = models.ForeignKey(Order, related_name="subscriptions", null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    start_date = models.DateField()
    end_date = models.DateField()
    coach_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.user.email} · {self.program.title}"


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    order = models.ForeignKey(Order, related_name="payments", on_delete=models.CASCADE)
    provider = models.CharField(max_length=40, default="unconfigured")
    transaction_id = models.CharField(max_length=120, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=8, default="USD")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    raw_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.provider} · {self.order.order_number}"
