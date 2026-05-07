from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.serializers import (
    PushConfigurationSerializer,
    PushSubscriptionDeactivateSerializer,
    PushSubscriptionSerializer,
)
from apps.notifications.services import deactivate_push_subscription


class PushConfigurationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = PushConfigurationSerializer.from_user(request.user)
        return Response(serializer.data)


class PushSubscriptionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PushSubscriptionSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save()
        return Response(
            {
                "id": str(subscription.id),
                "endpoint": subscription.endpoint,
                "is_active": subscription.is_active,
            },
            status=status.HTTP_201_CREATED,
        )


class PushSubscriptionDeactivateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PushSubscriptionDeactivateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = deactivate_push_subscription(user=request.user, endpoint=serializer.validated_data["endpoint"])
        return Response({"deactivated": updated > 0})

