from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def get_set_password_url(user):
    """
    Generates a URL to the password reset view that new users are linked to in an email.
    """
    return reverse(
        "wagtailadmin_password_reset_confirm",
        args=(
            urlsafe_base64_encode(force_bytes(user.pk)),
            default_token_generator.make_token(user),
        ),
    )
