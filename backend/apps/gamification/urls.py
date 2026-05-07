from django.urls import path

from .views import LevelHistoryView, StreakStatusView, WalletTransactionView, XPTransactionHistoryView, XPSummaryView

urlpatterns = [
    path("summary/", XPSummaryView.as_view(), name="xp-summary"),
    path("transactions/", XPTransactionHistoryView.as_view(), name="xp-transactions"),
    path("levels/", LevelHistoryView.as_view(), name="level-history"),
    path("wallet/", WalletTransactionView.as_view(), name="wallet-transactions"),
    path("streak/", StreakStatusView.as_view(), name="streak-status"),
]
