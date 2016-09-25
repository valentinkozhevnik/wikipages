from rest_framework import serializers
from .models import PagesStorage, PagesVersionStorage


class EditPagesSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=256)
    body = serializers.CharField()

    class Meta:
        model = PagesStorage
        fields = ['title', 'body']

    def create(self, validated_data):
        page = PagesStorage.objects.create()

        validated_data['page'] = page

        instance = PagesVersionStorage.objects.create(**validated_data)
        page.version = instance
        page.save()
        return page

    def update(self, instance: PagesStorage, validated_data):
        page = instance

        validated_data['page'] = page

        instance = PagesVersionStorage.objects.create(**validated_data)
        page.version = instance
        page.save()
        return page


class PagesListSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='version.title')
    body = serializers.CharField(source='version.body')

    class Meta:
        model = PagesStorage
        fields = ['id', 'title', 'body']


class PagesVersionListSerializer(serializers.ModelSerializer):

    class Meta:
        model = PagesVersionStorage
        fields = ['id', 'title', 'body', 'is_current']

