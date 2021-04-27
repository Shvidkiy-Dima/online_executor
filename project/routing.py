from django.urls import path, include
from channels.routing import URLRouter
from dashboard.routing import websocket_urlpatterns as dashboard_websocket_urlpatterns

websocket_urlpatterns = [
    path('ws/dashboard/', URLRouter(dashboard_websocket_urlpatterns)),
]