from django.contrib import admin

from .models import Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("client_name", "program_name", "rating", "is_featured")
    list_filter = ("is_featured", "rating")
    search_fields = ("client_name", "quote")
