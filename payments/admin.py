from django.contrib import admin

from .models import Order, OrderItem, Payment, Subscription
from .services import fulfill_paid_order


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.action(description="Mark paid and grant program access")
def mark_paid(modeladmin, request, queryset):
    for order in queryset:
        fulfill_paid_order(order, provider="manual-admin")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "full_name", "email", "amount", "status", "created_at")
    list_filter = ("status", "currency")
    search_fields = ("order_number", "email", "full_name")
    inlines = [OrderItemInline, PaymentInline]
    actions = [mark_paid]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "program", "status", "start_date", "end_date")
    list_filter = ("status", "program")
    search_fields = ("user__email",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "provider", "amount", "currency", "status", "created_at")
    list_filter = ("status", "provider")
    search_fields = ("order__order_number", "transaction_id")
