from rest_framework import serializers

from .models import Activity


class ActivitySerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = Activity
        fields = [
            "id",
            "title",
            "description",
            "category",
            "difficulty",
            "estimated_duration_minutes",
            "is_predefined",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["is_predefined", "created_by", "created_at"]

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        validated_data["is_predefined"] = False
        return super().create(validated_data)
