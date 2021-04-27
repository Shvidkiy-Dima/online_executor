from django.db import transaction
from rest_framework import serializers
from dashboard import models


class ModuleNestedSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Module
        fields = ('name', 'url', 'code', 'id')


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
        fields = ('name',  'folders', 'modules')


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Project
        fields = ('name', )

    def validate(self, attrs):
        user = self.context.get('request').user
        if user.projects.count() > 5:
            raise serializers.ValidationError('too many projects per user')

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
        fields = ('name', 'project', 'folder')

    def validate(self, attrs):
        project = attrs['project']
        folder = attrs.get('folder')
        if folder and folder.project != project:
            raise serializers.ValidationError('folder project mismatch')

        if project.modules.count() > 10:
            raise serializers.ValidationError('too many modules per project')

        return attrs
