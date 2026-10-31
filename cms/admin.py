from django.contrib import admin

from .models import SiteHome


@admin.register(SiteHome)
class SiteHomeAdmin(admin.ModelAdmin):
    list_display = ("id", "updated_at")
