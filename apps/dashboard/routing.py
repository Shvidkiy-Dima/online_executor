from django.urls import re_path, path
from dashboard import consumer

websocket_urlpatterns = [
    re_path(r"^module/(?P<module_id>.+)/$", consumer.ModuleConsumer.as_asgi()),
    path('common/', consumer.CommonConsumer.as_asgi())
]