from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, "user", None)
        if owner is None and hasattr(obj, "task"):
            owner = obj.task.user
        return request.user.is_staff or owner == request.user
