from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.tasks.models import Task
from apps.tasks.serializers import (
    AIClassificationPreviewSerializer,
    FinishTaskSessionSerializer,
    PauseTaskSessionSerializer,
    ResumeTaskSessionSerializer,
    StartTaskSessionSerializer,
    TaskCompletionSerializer,
    TaskSessionSerializer,
    TaskSerializer,
)
from apps.tasks.services import archive_task, refresh_task_ai
from apps.users.permissions import IsOwnerOrAdmin


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        return (
            Task.objects.filter(user=self.request.user, is_archived=False)
            .select_related("activity", "user", "completion", "session")
            .order_by("-planned_date", "planned_start_time", "-created_at")
        )

    def perform_create(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        if instance.status == Task.Status.COMPLETED or hasattr(instance, "completion"):
            archive_task(task=instance)
            return
        instance.delete()

    @action(detail=False, methods=["post"], url_path="preview-ai")
    def preview_ai(self, request):
        serializer = AIClassificationPreviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save())

    @action(detail=True, methods=["post"], url_path="start-session")
    def start_session(self, request, pk=None):
        task = self.get_object()
        serializer = StartTaskSessionSerializer(data=request.data, context={"task": task})
        serializer.is_valid(raise_exception=True)
        session = serializer.save()
        return Response({"session_id": str(session.id), "started_at": session.started_at}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="pause-session")
    def pause_session(self, request, pk=None):
        task = self.get_object()
        serializer = PauseTaskSessionSerializer(data=request.data, context={"task": task})
        serializer.is_valid(raise_exception=True)
        session = serializer.save()
        return Response(TaskSessionSerializer(session).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="resume-session")
    def resume_session(self, request, pk=None):
        task = self.get_object()
        serializer = ResumeTaskSessionSerializer(data=request.data, context={"task": task})
        serializer.is_valid(raise_exception=True)
        session = serializer.save()
        return Response(TaskSessionSerializer(session).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, pk=None):
        task = self.get_object()
        serializer = FinishTaskSessionSerializer(data=request.data, context={"task": task})
        serializer.is_valid(raise_exception=True)
        completion = serializer.save()
        return Response(TaskCompletionSerializer(completion).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="refresh-ai")
    def refresh_ai(self, request, pk=None):
        task = refresh_task_ai(task=self.get_object())
        return Response(self.get_serializer(task).data, status=status.HTTP_200_OK)
