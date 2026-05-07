from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="authuser", password="strongpass123", email="auth@example.com")

    def test_register_endpoint(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "strongpass123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_uses_email_and_password(self):
        response = self.client.post(
            reverse("login"),
            {"email": "auth@example.com", "password": "strongpass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_profile_requires_auth(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_patch_updates_reward_preference(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            reverse("profile"),
            {
                "reward_preference": "cafe_discount",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.reward_preference, "cafe_discount")

    def test_profile_includes_reward_member_id_and_progress(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["reward_member_id"].startswith("QB-"))
        self.assertEqual(response.data["reward_current_target_level"], 5)

    def test_reward_claim_unlocks_at_level_five_and_advances_target(self):
        self.client.force_authenticate(user=self.user)
        self.user.profile.level = 5
        self.user.profile.total_xp = 20000
        self.user.profile.reward_preference = "cafe_discount"
        self.user.profile.save(update_fields=["level", "total_xp", "reward_preference", "updated_at"])

        claim_response = self.client.post(reverse("reward-claim"), format="json")
        self.assertEqual(claim_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(claim_response.data["reward_level"], 5)
        self.assertEqual(claim_response.data["partner_name"], "Urth Caffe")
        self.assertTrue(claim_response.data["reward_member_id"].startswith("QB-"))

        profile_response = self.client.get(reverse("profile"))
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data["reward_claims_count"], 1)
        self.assertEqual(profile_response.data["reward_current_target_level"], 10)

    def test_reward_cannot_be_claimed_before_target_level(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse("reward-claim"), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
