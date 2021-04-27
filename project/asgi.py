import os
from django.core.asgi import get_asgi_application
from project.routing import websocket_urlpatterns
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from utils.middlewares import TokenAuthMiddlewareStack


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    'websocket': AllowedHostsOriginValidator(
                            TokenAuthMiddlewareStack(
                                URLRouter(websocket_urlpatterns)
                            )

                    )
                }
    )