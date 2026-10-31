from rest_framework import serializers

from .models import ProgressEntry, ProgressPhoto


class ProgressEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressEntry
        fields = ["id", "date", "weight", "body_fat", "chest", "waist", "arms", "legs", "notes"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        return ProgressEntry.objects.create(user=self.context["request"].user, **validated_data)


class ProgressPhotoSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = ProgressPhoto
        fields = ["id", "image", "url", "caption", "date"]
        read_only_fields = ["id", "url"]

    def get_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def create(self, validated_data):
        return ProgressPhoto.objects.create(user=self.context["request"].user, **validated_data)
