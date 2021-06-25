from django.db import transaction
from django.conf import settings
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from dashboard import models
from utils.sandbox import PackageAddSandBox
from dashboard.tasks import install_package


class ModuleNestedSerializer(serializers.ModelSerializer):

    url = serializers.CharField(source='get_url')

    class Meta:
        model = models.Module
        fields = ('name', 'url', 'id')


class FolderNestedSerializer(serializers.ModelSerializer):

    modules = ModuleNestedSerializer(many=True)

    class Meta:
        model = models.Folder
        fields = ('name', 'modules')


class ProjectDetailSerializer(serializers.ModelSerializer):
    folders = FolderNestedSerializer(many=True)
    modules = ModuleNestedSerializer(source='get_non_folder_modules', many=True)

    class Meta:
        model = models.Project
        fields = ('name',  'folders', 'modules', 'id')


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Project
        fields = ('name', 'id')

    def validate(self, attrs):
        user = self.context.get('request').user
        if user.projects.count() > 5:
            raise serializers.ValidationError('too many projects per user')

        if user.projects.filter(name__iexact=attrs['name']):
            raise serializers.ValidationError('project name must be unique')

        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            initial_module_name = 'main.py'
            project = super().create(validated_data)
            project.modules.create(name=initial_module_name)
            return project


class ModuleCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Module
        fields = ('name', 'project', 'folder', 'id')

    def validate(self, attrs):
        project = attrs['project']
        folder = attrs.get('folder')
        user = self.context.get('request').user

        if project.author != user:
            raise serializers.ValidationError('User is not owner')

        if folder and folder.project != project:
            raise serializers.ValidationError('folder project mismatch')

        if project.modules.count() > 10:
            raise serializers.ValidationError('too many modules per project')

        if not attrs['name'].endswith('.py'):
            attrs['name'] = f'{attrs["name"]}.py'

        return attrs


class ModuleDetailSerializer(ModuleNestedSerializer):
    code = serializers.CharField(source='code_as_str')

    class Meta(ModuleNestedSerializer.Meta):
        fields = ('code',) + ModuleNestedSerializer.Meta.fields


class PackageCreateSerializer(serializers.ModelSerializer):

    result = serializers.JSONField(read_only=True)
    name = serializers.CharField(write_only=True)

    class Meta:
        model = models.Package
        fields = ('name', 'result')

    def validate(self, attrs):
        user = self.context.get('request').user
        if user.packages.filter(name=attrs['name']).exists():
            raise serializers.ValidationError('Package already installed')

        if user.packages_size >= settings.MAX_PCG_STORAGE:
            raise serializers.ValidationError(
                f'max storage size is {settings.MAX_PCG_STORAGE}'
            )

        return attrs

    def create(self, validated_data):
        package_name = validated_data['name']
        user = self.context.get('request').user
        install_package.delay(user.id, package_name)
        return {}


class PackageSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Package
        fields = ('name', 'size', 'version', 'created', 'id')
