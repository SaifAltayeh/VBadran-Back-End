from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from programs.models import Gym

from .models import User


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "is_staff": self.user.is_staff,
        }
        return data


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=32, required=False, allow_blank=True)
    goal = serializers.CharField(max_length=255, required=False, allow_blank=True)
    gym_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value.lower()

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_gym_id(self, value):
        if value is None:
            return value
        if not Gym.objects.filter(pk=value, is_active=True).exists():
            raise serializers.ValidationError("Choose a gym.")
        return value

    def create(self, validated_data):
        phone = validated_data.pop("phone", "")
        goal = validated_data.pop("goal", "")
        gym_id = validated_data.pop("gym_id", None)
        user = User.objects.create_user(**validated_data)
        profile = user.profile
        changed = []
        if phone:
            profile.phone = phone
            changed.append("phone")
        if goal:
            profile.goal = goal
            changed.append("goal")
        if gym_id:
            profile.gym_id = gym_id
            changed.append("gym")
        if changed:
            profile.save(update_fields=changed)
        return user


class AccountSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    country = serializers.CharField(required=False, allow_blank=True)
    goal = serializers.CharField(required=False, allow_blank=True)
    fitness_level = serializers.CharField(required=False, allow_blank=True)
    gym_id = serializers.IntegerField(required=False, allow_null=True)
    gym = serializers.SerializerMethodField()

    def to_representation(self, instance):
        profile = instance.profile
        return {
            "id": instance.id,
            "email": instance.email,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "phone": profile.phone,
            "country": profile.country,
            "goal": profile.goal,
            "fitness_level": profile.fitness_level,
            "gym_id": profile.gym_id,
            "gym": None
            if not profile.gym_id
            else {
                "id": profile.gym_id,
                "name": profile.gym.name,
                "name_ar": profile.gym.name_ar,
                "slug": profile.gym.slug,
            },
        }

    def get_gym(self, instance):
        profile = instance.profile
        if not profile.gym_id:
            return None
        return {
            "id": profile.gym_id,
            "name": profile.gym.name,
            "name_ar": profile.gym.name_ar,
            "slug": profile.gym.slug,
        }

    def update(self, instance, validated_data):
        profile = instance.profile
        for field in ("first_name", "last_name"):
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()
        for field in ("phone", "country", "goal", "fitness_level"):
            if field in validated_data:
                setattr(profile, field, validated_data[field])
        if "gym_id" in validated_data:
            profile.gym_id = validated_data["gym_id"]
        profile.save()
        return instance


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_password(self, value):
        validate_password(value, self.context["request"].user)
        return value

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField()

    def validate_password(self, value):
        validate_password(value)
        return value
