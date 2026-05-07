from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/auth/", include("apps.users.urls")),
    path("api/v1/activities/", include("apps.activities.urls")),
    path("api/v1/tasks/", include("apps.tasks.urls")),
    path("api/v1/gamification/", include("apps.gamification.urls")),
    path("api/v1/leaderboard/", include("apps.leaderboard.urls")),
    path("api/v1/notifications/", include("apps.notifications.urls")),
    path("api/v1/reports/", include("apps.reports.urls")),
]
