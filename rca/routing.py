from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from content_locking import routing
from django.urls import path

application = ProtocolTypeRouter(
    {"websocket": AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns))}
)
