from django.contrib import admin

from .models import Gym, Package, Program, ProgramFAQ, ProgramFeature


@admin.register(Gym)
class GymAdmin(admin.ModelAdmin):
    list_display = ("name", "name_ar", "slug", "is_active", "order")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}


class ProgramFeatureInline(admin.TabularInline):
    model = ProgramFeature
    extra = 1


class ProgramFAQInline(admin.TabularInline):
    model = ProgramFAQ
    extra = 1


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "price", "duration_weeks", "is_featured", "is_active")
    list_filter = ("category", "is_featured", "is_active", "difficulty")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProgramFeatureInline, ProgramFAQInline]


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ("name", "gym", "price", "duration_weeks", "is_highlighted", "is_active")
    list_filter = ("is_highlighted", "is_active", "gym")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
