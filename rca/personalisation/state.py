from dataclasses import dataclass

from django.http import HttpRequest


@dataclass(slots=True)
class PersonalisationState:
    """Request-local rendering and cache eligibility, private by default."""

    defer_personalisation: bool = False
    private: bool = True
    anonymous_cache_marker_eligible: bool = False


def get_personalisation_state(request: HttpRequest) -> PersonalisationState:
    """Default to private inline rendering when the page hook has not run."""
    state = getattr(request, "_personalisation_state", None)
    if state is None:
        state = PersonalisationState()
        request._personalisation_state = state
    return state
