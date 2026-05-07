from __future__ import annotations

import secrets

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .models import RewardClaim, UserProfile
from config.settings import DEFAULT_FROM_EMAIL, FRONTEND_URL

User = get_user_model()
XP_PER_LEVEL = 500
REWARD_LEVEL_STEP = 5

BOOK_REWARD_SEQUENCE = [
    ("Free Book Reward", "Partner book desk"),
]

CAFE_REWARD_SEQUENCE = [
    ("20% Discount", "Urth Caffe"),
    ("20% Discount", "Pete's Cafe"),
    ("20% Discount", "Alou Beirut"),
]


@transaction.atomic
def register_user(*, username: str, email: str, password: str, first_name: str = "", last_name: str = "") -> User:
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
    return user


def send_password_reset_email(*, user: User) -> None:
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_link = f"{FRONTEND_URL}/reset-password?uid={uid}&token={token}"
    send_mail(
        subject="Reset your productivity account password",
        message=f"Use this link to reset your password: {reset_link}",
        from_email=DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def reset_password(*, uid: str, token: str, password: str) -> User:
    user_id = urlsafe_base64_decode(uid).decode()
    user = User.objects.get(pk=user_id)
    if not default_token_generator.check_token(user, token):
        raise ValueError("Invalid or expired token.")
    user.set_password(password)
    user.save(update_fields=["password"])
    return user


def ensure_reward_member_id(*, profile: UserProfile) -> UserProfile:
    if profile.reward_member_id:
        return profile

    while True:
        candidate = f"QB-{secrets.token_hex(4).upper()}"
        if not UserProfile.objects.filter(reward_member_id=candidate).exists():
            profile.reward_member_id = candidate
            profile.save(update_fields=["reward_member_id", "updated_at"])
            return profile


def get_reward_claim_count(*, user) -> int:
    return RewardClaim.objects.filter(user=user).count()


def get_current_reward_target_level(*, user) -> int:
    return (get_reward_claim_count(user=user) + 1) * REWARD_LEVEL_STEP


def get_reward_xp_target(*, level: int) -> int:
    return (level - 1) * XP_PER_LEVEL


def get_reward_offer(*, reward_preference: str, level: int) -> dict[str, str]:
    if reward_preference == UserProfile.RewardPreference.CAFE_DISCOUNT:
        sequence = CAFE_REWARD_SEQUENCE
        reward_title = "Cafe / Restaurant Discount"
    else:
        sequence = BOOK_REWARD_SEQUENCE
        reward_title = "Book Reward"

    milestone_index = max(0, (level // REWARD_LEVEL_STEP) - 1)
    offer_title, partner_name = sequence[milestone_index % len(sequence)]

    if reward_preference == UserProfile.RewardPreference.CAFE_DISCOUNT:
        instructions = (
            f"Show your Reward ID at {partner_name} and tell the team you unlocked your Questboard level {level} reward "
            f"to receive your {offer_title.lower()}."
        )
    else:
        instructions = (
            f"Show your Reward ID at the {partner_name} and tell the team you unlocked your Questboard level {level} reward "
            f"to collect your free book."
        )

    return {
        "reward_title": reward_title,
        "partner_name": partner_name,
        "offer_title": offer_title,
        "instructions": instructions,
    }


def get_reward_progress(*, profile: UserProfile) -> dict:
    ensure_reward_member_id(profile=profile)
    target_level = get_current_reward_target_level(user=profile.user)
    target_xp = get_reward_xp_target(level=target_level)
    current_xp = profile.total_xp
    return {
        "reward_claims_count": get_reward_claim_count(user=profile.user),
        "reward_current_target_level": target_level,
        "reward_current_target_xp": target_xp,
        "reward_xp_remaining": max(0, target_xp - current_xp),
        "reward_levels_remaining": max(0, target_level - profile.level),
        "reward_can_claim": profile.level >= target_level,
    }


@transaction.atomic
def claim_current_reward(*, user) -> RewardClaim:
    profile = UserProfile.objects.select_for_update().get(user=user)
    ensure_reward_member_id(profile=profile)
    target_level = get_current_reward_target_level(user=user)
    if profile.level < target_level:
        raise ValueError(f"Reach level {target_level} before claiming this reward.")

    offer = get_reward_offer(reward_preference=profile.reward_preference, level=target_level)
    claim, created = RewardClaim.objects.get_or_create(
        user=user,
        reward_preference=profile.reward_preference,
        reward_level=target_level,
        defaults={
            "reward_title": offer["reward_title"],
            "partner_name": offer["partner_name"],
            "instructions": offer["instructions"],
        },
    )
    if not created:
        raise ValueError("This reward has already been claimed.")
    return claim
