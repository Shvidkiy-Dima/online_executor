from rest_framework import generics, permissions
from rest_framework.response import Response
from dashboard import models
from dashboard import serializers
from utils.sandbox import SandBox, Volume
from utils.functions import get_dir_size
import epicbox


class ProjectView(generics.ListCreateAPIView):
    serializer_class = serializers.ProjectSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.projects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.ProjectDetailSerializer

    def get_queryset(self):
        return self.request.user.projects.all()


class ModuleCreateView(generics.CreateAPIView):
    serializer_class = serializers.ModuleCreateSerializer


class StartModuleView(generics.GenericAPIView):
    queryset = models.Module.objects.all()

    def post(self, request, *args, **kwargs):
        module = self.get_object()
        user = request.user
        epicbox.configure(
            profiles=[
                epicbox.Profile('python', 'python:3.8-alpine')
            ]
        )

        files = [{'name': 'main.py', 'content': module.code}]
        limits = {'cputime': 1, 'memory': 64, 'realtime': 5}

        workdir = '/sandbox'
        volume = Volume(user.venv_path, f'{workdir}/venv', 'ro')
        sandbox = SandBox(volume=volume, workdir=workdir)
        result = sandbox.run('python', f'{workdir}/venv/bin/python3 main.py', files=files, limits=limits)

        return Response(result)


# class AddModule(generics.CreateAPIView):
#
#     def create(self, request, *args, **kwargs):
#         user = request.user
#         cur_size = get_dir_size(user.venv_path)
#         if cur_size > 250 * 1024:
#             raise RuntimeError
#
#         workdir = '/sandbox'
#         volume = Volume(user.venv_path, f'{workdir}/venv', 'rw')
#         sandbox = SandBox(volume=volume, workdir=workdir)
#         limits = {'cputime': 1, 'memory': 64, 'realtime': 5}
#
#         b"""
#         import pip
#         pip.main(['download', package])
#
#
#         """
#
#         files = [{'name': 'main.py', 'content': ''}]
#         result = sandbox.run('python', f'{workdir}/venv/bin/pip main.py',
#                              files=files, limits=limits)


