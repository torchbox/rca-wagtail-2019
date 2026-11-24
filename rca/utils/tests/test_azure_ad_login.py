from django.contrib.auth.models import Group
from django.test import TestCase

from social_core.backends.azuread_tenant import AzureADTenantOAuth2
from social_django.models import UserSocialAuth
from social_django.utils import load_strategy


class AzureADLoginTests(TestCase):
    """
    Log in through our SOCIAL_AUTH_PIPELINE with a stubbed Azure AD tenant
    response and check what ends up on the user.

    Name handling itself is tested in social-auth-core and
    social-auth-app-django with a dummy backend and the default pipeline.
    These tests cover our custom behaviour: the tenant backend's claim
    mapping, our pipeline's steps, and make_sso_users_editors.
    """

    def setUp(self):
        self.editors, _ = Group.objects.get_or_create(name="Editors")

    def login(self, **claims):
        response = {"sub": "azure-sub-1", "upn": "jane@example.com", **claims}
        strategy = load_strategy()
        backend = AzureADTenantOAuth2(strategy=strategy)
        return strategy.authenticate(backend=backend, response=response)

    def test_first_login_creates_editor_from_azure_claims(self):
        user = self.login(name="Jane Smith", given_name="Jane", family_name="Smith")

        user.refresh_from_db()
        self.assertEqual(user.first_name, "Jane")
        self.assertEqual(user.last_name, "Smith")
        self.assertEqual(user.email, "jane@example.com")
        self.assertIn(self.editors, user.groups.all())
        self.assertTrue(
            UserSocialAuth.objects.filter(
                user=user, provider=AzureADTenantOAuth2.name, uid="azure-sub-1"
            ).exists()
        )

    def test_login_without_name_claims_keeps_stored_names(self):
        # Before social-auth-core 6.x the tenant backend turned missing claims
        # into "", which wiped stored names on the next login.
        user = self.login(name="Jane Smith", given_name="Jane", family_name="Smith")
        self.login()

        user.refresh_from_db()
        self.assertEqual(user.first_name, "Jane")
        self.assertEqual(user.last_name, "Smith")

    def test_full_name_only_is_split_into_first_and_last(self):
        # Fails if social_names is missing from SOCIAL_AUTH_PIPELINE.
        user = self.login(name="Jane Smith")

        user.refresh_from_db()
        self.assertEqual(user.first_name, "Jane")
        self.assertEqual(user.last_name, "Smith")
