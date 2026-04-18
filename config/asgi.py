# """
# ASGI config for config project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
# """

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# application = get_asgi_application()


import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from apps.realtime.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings.dev")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),   # 👈 keep this
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
