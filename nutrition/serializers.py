from rest_framework import serializers

from .models import Meal, NutritionDay, NutritionNote, NutritionPlan


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ["id", "name", "suggestion"]


class NutritionDaySerializer(serializers.ModelSerializer):
    meals = MealSerializer(many=True, read_only=True)

    class Meta:
        model = NutritionDay
        fields = ["id", "name", "meals"]


class NutritionNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionNote
        fields = ["id", "body"]


class NutritionPlanSerializer(serializers.ModelSerializer):
    days = NutritionDaySerializer(many=True, read_only=True)
    notes = NutritionNoteSerializer(many=True, read_only=True)

    class Meta:
        model = NutritionPlan
        fields = [
            "id",
            "title",
            "overview",
            "calories",
            "protein_g",
            "carbs_g",
            "fats_g",
            "coach_notes",
            "download_label",
            "download_url",
            "days",
            "notes",
        ]
