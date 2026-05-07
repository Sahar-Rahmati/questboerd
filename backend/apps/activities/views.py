from django.db.models import Q
from rest_framework import mixins, permissions, viewsets

from .models import Activity
from .serializers import ActivitySerializer


class ActivityViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ActivitySerializer

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        return Activity.objects.filter(Q(is_predefined=True) | Q(created_by=user)).order_by("category", "title")
