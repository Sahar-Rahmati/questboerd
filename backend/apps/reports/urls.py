from django.urls import path

from .views import CategoryBreakdownView, WeeklyReportView, WeeklyXPChartView

urlpatterns = [
    path("weekly/", WeeklyReportView.as_view(), name="weekly-report"),
    path("weekly-chart/", WeeklyXPChartView.as_view(), name="weekly-chart"),
    path("category-breakdown/", CategoryBreakdownView.as_view(), name="category-breakdown"),
]
