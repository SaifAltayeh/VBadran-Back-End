from django.contrib import admin

from .models import ContactInquiry


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "program", "status", "created_at")
    list_filter = ("status", "fitness_level")
    search_fields = ("name", "email", "message")
    readonly_fields = ("created_at",)
