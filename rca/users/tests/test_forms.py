from django.test import TestCase
from django.urls import reverse
from wagtail.test.utils import WagtailTestUtils

from rca.users.forms import CustomUserEditForm
from rca.users.viewsets import UserViewSet


class TestUserFormHelpers(TestCase):
    def test_get_user_edit_form_with_default_form(self):
        user_form = UserViewSet().get_form_class(for_update=True)
        self.assertIs(user_form, CustomUserEditForm)


class TestUserEditView(TestCase, WagtailTestUtils):
    def setUp(self):
        # Create a user to edit
        self.test_user = self.create_user(
            username="testuser",
            email="testuser@email.com",
            first_name="Original",
            last_name="User",
            password="password",
        )
        # Login
        self.current_user = self.login()

    def get(self, params={}, user_id=None):
        return self.client.get(
            reverse("wagtailusers_users:edit", args=(user_id or self.test_user.pk,)),
            params,
        )

    def post(self, post_data={}, user_id=None):
        return self.client.post(
            reverse("wagtailusers_users:edit", args=(user_id or self.test_user.pk,)),
            post_data,
        )

    def test_username_field_is_locked(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "wagtailusers/users/edit.html")
        self.assertContains(
            response,
            '<input type="text" name="username" value="testuser" readonly maxlength="150"'
            ' aria-describedby="id_username-helptext" required id="id_username">',
        )
