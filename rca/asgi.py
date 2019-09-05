from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from content_locking import routing

application = ProtocolTypeRouter(
    {"websocket": AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns))}
)
