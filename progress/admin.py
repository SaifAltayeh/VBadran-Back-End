from django.contrib import admin

from .models import ProgressEntry, ProgressPhoto


@admin.register(ProgressEntry)
class ProgressEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "weight", "waist", "chest")
    list_filter = ("date",)
    search_fields = ("user__email",)


@admin.register(ProgressPhoto)
class ProgressPhotoAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "caption")
    search_fields = ("user__email",)
