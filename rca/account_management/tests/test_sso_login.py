import re

from django.test import Client, TestCase, override_settings
from django.urls import reverse

BEGIN_URL = reverse("social:begin", args=["azuread-tenant-oauth2"])


@override_settings(
    SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_KEY="client-id",
    SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_SECRET="client-secret",
    SOCIAL_AUTH_AZUREAD_TENANT_OAUTH2_TENANT_ID="tenant-id",
)
class TestSingleSignOnLogin(TestCase):
    """
    social-auth-app-django 6+ only accepts POST (with a CSRF token) on
    social:begin, so the SSO button must be a CSRF-protected form.
    """

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def test_admin_login_sso_form_starts_sso(self):
        response = self.client.get("/admin/login/")
        self.assertEqual(response.status_code, 200)
        forms = re.findall(
            r'<form[^>]*action="' + re.escape(BEGIN_URL) + r'"[^>]*>(.*?)</form>',
            response.content.decode(),
            re.DOTALL,
        )
        self.assertEqual(len(forms), 1)
        fields = dict(
            re.findall(r'<input type="hidden" name="([^"]+)" value="([^"]*)"', forms[0])
        )
        self.assertIn("csrfmiddlewaretoken", fields)

        response = self.client.post(BEGIN_URL, fields)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response["Location"].startswith(
                "https://login.microsoftonline.com/tenant-id/"
            )
        )

    def test_get_on_begin_is_rejected(self):
        response = self.client.get(BEGIN_URL)
        self.assertEqual(response.status_code, 405)
