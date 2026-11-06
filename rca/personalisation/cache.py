from .state import get_personalisation_state


def can_defer_personalisation(page, request):
    """Defer CTAs only for unrestricted anonymous page requests."""
    from wagtail.contrib.forms.models import FormMixin

    if (
        request.method not in ("GET", "HEAD")
        or request.user.is_authenticated
        or getattr(request, "is_preview", False)
        or isinstance(page, FormMixin)
    ):
        return False

    # Evaluate the queryset so Wagtail's later access check can reuse it.
    return not page.get_view_restrictions()


def can_share_page_response(request, *, has_personalised_ctas):
    """Require explicit deferral before allowing a page response to be shared.

    Inline personalisation touches the session even when no CTA matches.
    """
    state = get_personalisation_state(request)
    return (
        state.defer_personalisation
        and not has_personalised_ctas
        and not request.user.is_authenticated
        and not getattr(request, "is_preview", False)
        and not state.private
    )
