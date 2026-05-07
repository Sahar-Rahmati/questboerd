from django.urls import path

from apps.notifications.views import (
    PushConfigurationView,
    PushSubscriptionDeactivateView,
    PushSubscriptionView,
)

urlpatterns = [
    path("push-config/", PushConfigurationView.as_view(), name="push-config"),
    path("subscriptions/", PushSubscriptionView.as_view(), name="push-subscription"),
    path("subscriptions/deactivate/", PushSubscriptionDeactivateView.as_view(), name="push-subscription-deactivate"),
]

