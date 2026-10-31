from django.db import models


class Program(models.Model):
    class Difficulty(models.TextChoices):
        ALL = "all", "All levels"
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    class Category(models.TextChoices):
        PERSONAL = "personal-training", "Personal Training"
        ONLINE = "online-coaching", "Online Coaching"
        TRANSFORMATION = "body-transformation", "Body Transformation"
        TRAINING = "training-plans", "Training Plans"
        NUTRITION = "nutrition", "Nutrition Guidance"
        COMBINED = "training-nutrition", "Training + Nutrition"
        SPORTS = "custom-sports", "Custom Sports Programs"

    title = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    short_description = models.TextField()
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=8, default="USD")
    duration_weeks = models.PositiveIntegerField()
    difficulty = models.CharField(max_length=24, choices=Difficulty.choices, default=Difficulty.ALL)
    category = models.CharField(max_length=40, choices=Category.choices)
    goal = models.CharField(max_length=180)
    featured_image = models.CharField(max_length=255, blank=True)
    image_alt = models.CharField(max_length=255, blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    includes_nutrition = models.BooleanField(default=False)
    includes_training = models.BooleanField(default=True)
    expected_outcome = models.TextField(blank=True)
    who_for = models.TextField(blank=True)
    training_structure = models.TextField(blank=True)
    nutrition_overview = models.TextField(blank=True)
    support_overview = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.title


class ProgramFeature(models.Model):
    program = models.ForeignKey(Program, related_name="features", on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text


class ProgramFAQ(models.Model):
    program = models.ForeignKey(Program, related_name="faqs", on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.question


class Package(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField(unique=True)
    tagline = models.CharField(max_length=180)
    description = models.TextField()
    duration_weeks = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=8, default="USD")
    expected_outcome = models.TextField()
    is_highlighted = models.BooleanField(default=False)
    program = models.ForeignKey(Program, related_name="packages", null=True, blank=True, on_delete=models.SET_NULL)
    training_plan = models.BooleanField(default=True)
    nutrition = models.BooleanField(default=False)
    weekly_checkins = models.BooleanField(default=False)
    video_library = models.BooleanField(default=True)
    coach_support = models.BooleanField(default=False)
    progress_tracking = models.BooleanField(default=True)
    program_adjustments = models.BooleanField(default=False)
    messaging = models.BooleanField(default=False)
    support_label = models.CharField(max_length=80, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name
