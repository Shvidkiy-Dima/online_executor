from celery import shared_task
from account.models import User
from utils.sandbox import PackageAddSandBox
from django.db import transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from dashboard import models


def get_out(out):
    try:
        return out.decode('utf8')
    except Exception:
        return 'Not serializable'


@shared_task
def install_package(user_id, package_name):
    from dashboard.serializers import PackageSerializer
    
    user = User.objects.get(id=user_id)
    result = PackageAddSandBox(package_name, user).run()
    layer = get_channel_layer()

    data = {'stdout': get_out(result['stdout']),'stderr': get_out(result['stderr']) }
    if result['exit_code'] != 0:
        data['success'] = False
    else:
        data['success'] = True
        with transaction.atomic():
            size, version = result['stdout'].decode().split('|')
            p = models.Package.objects.create(name=package_name,
                                          size=int(size), user=user,
                                          version=version or None)

            data['package'] = PackageSerializer(p).data

    async_to_sync(layer.group_send)(str(user), {'type': 'send_package', 'data': data})
