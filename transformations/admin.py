from django.contrib import admin

from .models import Transformation


@admin.register(Transformation)
class TransformationAdmin(admin.ModelAdmin):
    list_display = ("client_name", "program_name", "duration_weeks", "is_featured")
    list_filter = ("is_featured", "program")
    search_fields = ("client_name", "slug", "result_summary")
    prepopulated_fields = {"slug": ("client_name",)}
