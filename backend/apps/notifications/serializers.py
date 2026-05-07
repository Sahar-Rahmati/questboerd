from rest_framework import serializers

from apps.notifications.models import PushSubscription
from apps.notifications.services import get_push_configuration, save_push_subscription


class PushKeysSerializer(serializers.Serializer):
    p256dh = serializers.CharField()
    auth = serializers.CharField()


class PushSubscriptionSerializer(serializers.Serializer):
    endpoint = serializers.URLField(max_length=2000)
    expiration_time = serializers.IntegerField(required=False, allow_null=True)
    keys = PushKeysSerializer()

    def create(self, validated_data):
        request = self.context["request"]
        return save_push_subscription(
            user=request.user,
            endpoint=validated_data["endpoint"],
            p256dh_key=validated_data["keys"]["p256dh"],
            auth_key=validated_data["keys"]["auth"],
            expiration_time=validated_data.get("expiration_time"),
            user_agent=request.headers.get("User-Agent", ""),
        )


class PushSubscriptionDeactivateSerializer(serializers.Serializer):
    endpoint = serializers.URLField(max_length=2000)


class PushConfigurationSerializer(serializers.Serializer):
    vapid_public_key = serializers.CharField(allow_blank=True)
    is_configured = serializers.BooleanField()
    has_active_subscription = serializers.BooleanField()

    @classmethod
    def from_user(cls, user):
        return cls(get_push_configuration(user=user))

