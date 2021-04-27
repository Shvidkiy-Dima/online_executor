from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from dashboard.models import Module


class ModuleConsumer(AsyncJsonWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        self.group_name = None
        self.user = None
        self.module = None
        super().__init__(*args, **kwargs)

    async def connect(self):
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close()
            return

        project_id = self.scope["url_route"]["kwargs"]["module_id"]
        module = await self._get_module(user, project_id)
        if not module:
            await self.close()
            return

        self.group_name = f'module_{module.id}-{user}'
        self.user = user
        self.module = module
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if self.group_name is not None:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content: dict, **kwargs):
        await self._add_to_module(content['code'])

    @database_sync_to_async
    def _add_to_module(self, code):
        self.module.code = code.encode()
        self.module.save(update_fields=['code'])

    @database_sync_to_async
    def _get_module(self, user, module_id):
        return Module.objects.filter(project__author=user, id=module_id).first()
