from django.db import models

from programs.models import Program


class NutritionPlan(models.Model):
    program = models.OneToOneField(Program, related_name="nutrition_plan", on_delete=models.CASCADE)
    title = models.CharField(max_length=160)
    overview = models.TextField()
    calories = models.PositiveIntegerField(null=True, blank=True)
    protein_g = models.PositiveIntegerField(null=True, blank=True)
    carbs_g = models.PositiveIntegerField(null=True, blank=True)
    fats_g = models.PositiveIntegerField(null=True, blank=True)
    coach_notes = models.TextField(blank=True)
    download_label = models.CharField(max_length=120, blank=True)
    download_url = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title


class NutritionDay(models.Model):
    plan = models.ForeignKey(NutritionPlan, related_name="days", on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class Meal(models.Model):
    day = models.ForeignKey(NutritionDay, related_name="meals", on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    suggestion = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class NutritionNote(models.Model):
    plan = models.ForeignKey(NutritionPlan, related_name="notes", on_delete=models.CASCADE)
    body = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
