from django.conf import settings
from django.db import models

from apps.common.models import TimestampedModel


class UserProfile(TimestampedModel):
    class RewardPreference(models.TextChoices):
        BOOKSTORE = "bookstore", "Book Reward"
        CAFE_DISCOUNT = "cafe_discount", "Cafe / Restaurant Discount"
        STUDY_CAFE = "study_cafe", "Legacy Study Cafe"
        GYM_POOL = "gym_pool", "Legacy Gym / Pool"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    total_xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    streak_count = models.PositiveIntegerField(default=0)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wallet_cardholder_name = models.CharField(max_length=255, blank=True)
    wallet_card_brand = models.CharField(max_length=50, blank=True)
    wallet_card_last4 = models.CharField(max_length=4, blank=True)
    wallet_card_expiry_month = models.PositiveSmallIntegerField(null=True, blank=True)
    wallet_card_expiry_year = models.PositiveSmallIntegerField(null=True, blank=True)
    apple_pay_enabled = models.BooleanField(default=False)
    samsung_pay_enabled = models.BooleanField(default=False)
    wallet_permissions_granted = models.BooleanField(default=False)
    reward_preference = models.CharField(max_length=30, choices=RewardPreference.choices, default=RewardPreference.BOOKSTORE)
    reward_member_id = models.CharField(max_length=32, unique=True, blank=True)

    class Meta:
        ordering = ["-total_xp", "user__date_joined"]

    def __str__(self) -> str:
        return f"{self.user.username} profile"


class RewardClaim(TimestampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reward_claims")
    reward_preference = models.CharField(max_length=30)
    reward_level = models.PositiveIntegerField()
    reward_title = models.CharField(max_length=255)
    partner_name = models.CharField(max_length=255)
    instructions = models.TextField()

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "reward_preference", "reward_level"],
                name="unique_reward_claim_per_user_preference_level",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user.username} reward claim for level {self.reward_level}"
