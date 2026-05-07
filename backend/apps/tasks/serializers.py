from rest_framework import serializers

from apps.ai_engine.services import estimate_xp
from apps.tasks.models import Task, TaskCompletion, TaskSession
from apps.tasks.services import (
    calculate_session_elapsed_seconds,
    create_task_with_ai,
    finish_task_session,
    get_ai_preview,
    pause_task_session,
    resume_task_session,
    start_task_session,
)


class NestedTaskCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskCompletion
        fields = ["id", "actual_duration_minutes", "earned_xp", "xp_breakdown", "completed_at"]


class TaskSessionSerializer(serializers.ModelSerializer):
    is_active = serializers.SerializerMethodField()
    is_paused = serializers.SerializerMethodField()
    is_running = serializers.SerializerMethodField()
    elapsed_seconds = serializers.SerializerMethodField()

    class Meta:
        model = TaskSession
        fields = [
            "id",
            "started_at",
            "paused_at",
            "ended_at",
            "accumulated_seconds",
            "tracked_duration_minutes",
            "elapsed_seconds",
            "is_active",
            "is_paused",
            "is_running",
        ]

    def get_is_active(self, obj):
        return obj.ended_at is None

    def get_is_paused(self, obj):
        return obj.ended_at is None and obj.paused_at is not None

    def get_is_running(self, obj):
        return obj.ended_at is None and obj.paused_at is None

    def get_elapsed_seconds(self, obj):
        return calculate_session_elapsed_seconds(obj)


class AIClassificationPreviewSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    planned_start_time = serializers.TimeField(required=False)
    planned_end_time = serializers.TimeField(required=False)

    def validate(self, attrs):
        start = attrs.get("planned_start_time")
        end = attrs.get("planned_end_time")
        if end and not start:
            raise serializers.ValidationError("Start time is required if you provide an end time.")
        if start and end and end <= start:
            raise serializers.ValidationError("End time must be after start time.")
        return attrs

    def create(self, validated_data):
        return get_ai_preview(**validated_data)


class TaskSerializer(serializers.ModelSerializer):
    activity = serializers.UUIDField(source="activity_id", read_only=True)
    estimated_xp = serializers.SerializerMethodField()
    activity_details = serializers.SerializerMethodField()
    completion = NestedTaskCompletionSerializer(read_only=True)
    session = TaskSessionSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "activity",
            "activity_details",
            "title",
            "description",
            "planned_date",
            "planned_start_time",
            "planned_end_time",
            "status",
            "ai_detected_category",
            "ai_detected_difficulty",
            "ai_estimated_duration_minutes",
            "ai_multiplier",
            "ai_explanation",
            "anomaly_flags",
            "estimated_xp",
            "session",
            "completion",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "ai_detected_category",
            "ai_detected_difficulty",
            "ai_estimated_duration_minutes",
            "ai_multiplier",
            "ai_explanation",
            "anomaly_flags",
            "estimated_xp",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "planned_date": {"required": False},
            "planned_start_time": {"required": False},
            "planned_end_time": {"required": False},
        }

    def get_estimated_xp(self, obj):
        return estimate_xp(
            actual_duration_minutes=obj.ai_estimated_duration_minutes,
            detected_difficulty=obj.ai_detected_difficulty,
            ai_multiplier=float(obj.ai_multiplier),
        )

    def get_activity_details(self, obj):
        activity = obj.activity
        return {
            "id": str(activity.id),
            "title": activity.title,
            "category": activity.category,
            "difficulty": activity.difficulty,
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)
        start = attrs.get("planned_start_time", getattr(self.instance, "planned_start_time", None))
        end = attrs.get("planned_end_time", getattr(self.instance, "planned_end_time", None))
        if end and not start:
            raise serializers.ValidationError("Planned start time is required if an end time is provided.")
        if start and end and end <= start:
            raise serializers.ValidationError("Planned end time must be after planned start time.")
        return attrs

    def validate_status(self, value: str):
        if value == Task.Status.COMPLETED:
            raise serializers.ValidationError("Use the complete endpoint to complete a task.")
        return value

    def create(self, validated_data):
        return create_task_with_ai(user=self.context["request"].user, **validated_data)


class TaskCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskCompletion
        fields = ["id", "actual_duration_minutes", "earned_xp", "xp_breakdown", "completed_at"]
        read_only_fields = ["earned_xp", "xp_breakdown", "completed_at"]


class StartTaskSessionSerializer(serializers.Serializer):
    def save(self, **kwargs):
        task = self.context["task"]
        try:
            return start_task_session(task=task)
        except ValueError as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc


class FinishTaskSessionSerializer(serializers.Serializer):
    def save(self, **kwargs):
        task = self.context["task"]
        try:
            return finish_task_session(task=task)
        except ValueError as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc


class PauseTaskSessionSerializer(serializers.Serializer):
    def save(self, **kwargs):
        task = self.context["task"]
        try:
            return pause_task_session(task=task)
        except ValueError as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc


class ResumeTaskSessionSerializer(serializers.Serializer):
    def save(self, **kwargs):
        task = self.context["task"]
        try:
            return resume_task_session(task=task)
        except ValueError as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc
