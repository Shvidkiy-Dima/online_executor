import json
from rest_framework import generics, permissions
from django.http.response import HttpResponse
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from dashboard import models
from dashboard import serializers
from utils.sandbox import PackageAddSandBox, ModuleRunSandBox, \
    PackageRemoveSandBox, ModuleRunAPISandBox
from utils.views import SerializerMapMixin


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


class ModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.ModuleDetailSerializer

    def get_queryset(self):
        return models.Module.objects.filter(project__author=self.request.user)

    def perform_destroy(self, instance):
        if instance.project.modules.count() == 1:
            raise ValidationError('Project must have at least one module')

        return super().perform_destroy(instance)


class ModuleRunView(generics.GenericAPIView):
    queryset = models.Module.objects.all()

    def get_queryset(self):
        return models.Module.objects.filter(project__author=self.request.user)

    def post(self, request, *args, **kwargs):
        module = self.get_object()
        user = request.user
        result = ModuleRunSandBox(module, user).run()
        return Response(result)


class ModuleRunApiView(generics.GenericAPIView):
    queryset = models.Module.objects.all()

    def get_queryset(self):
        return models.Module.objects.filter(project__author=self.request.user)

    def post(self, request, *args, **kwargs):
        module = self.get_object()
        user = request.user
        result = ModuleRunAPISandBox(module, user).run()
        return self.get_response(result)

    def get_response(self, result):
        if result['exit_code'] == 0:
            data = json.loads(result['stdout'].decode('utf8'))
            response_class = Response if data['type'] == 'json' else HttpResponse
            body = json.loads(data['body']) if data['type'] == 'json' else data['body']
            response = response_class(data=body, status=data['status_code'])
        else:
            body = {'error': result['stderr'].decode('utf8')}
            response = Response(body, status=404)
        return response


class PackageView(SerializerMapMixin, generics.ListCreateAPIView):
    serializer_map = {'post': serializers.PackageCreateSerializer,
                      'get': serializers.PackageSerializer
                      }

    def get_queryset(self):
        return self.request.user.packages.all()


class PackageDetailView(generics.DestroyAPIView):

    def get_queryset(self):
        return self.request.user.packages.all()

    def perform_destroy(self, instance):
        result = PackageRemoveSandBox(instance.name, self.request.user).run()
        if result['exit_code'] == 0:
            return instance.delete()

        else:
            raise ValidationError(result['stderr'].decode())

