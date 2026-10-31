from django.contrib import admin

from .models import Meal, NutritionDay, NutritionNote, NutritionPlan


class MealInline(admin.TabularInline):
    model = Meal
    extra = 1


class NutritionDayInline(admin.StackedInline):
    model = NutritionDay
    extra = 0
    show_change_link = True


class NutritionNoteInline(admin.TabularInline):
    model = NutritionNote
    extra = 1


@admin.register(NutritionPlan)
class NutritionPlanAdmin(admin.ModelAdmin):
    list_display = ("title", "program", "calories", "protein_g")
    inlines = [NutritionNoteInline, NutritionDayInline]


@admin.register(NutritionDay)
class NutritionDayAdmin(admin.ModelAdmin):
    list_display = ("name", "plan")
    inlines = [MealInline]
