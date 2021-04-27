from django.urls import re_path
from dashboard import consumer

websocket_urlpatterns = [
    re_path(r"^module/(?P<module_id>\w+)/$", consumer.ModuleConsumer.as_asgi())
]