def get_client_real_ip(request):
    """
    Gets the IP address of whatever is sending the request, ignoring X-Forwarded-For header.

    We use the basic-auth-ip-whitelist plugin to prevent direct access to the backend webserver.
    The builtin get_client_ip function will use X-Forwarded-For if provided, but we want to check
    against the real IP address instead.
    """
    return request.META.get("REMOTE_ADDR")
