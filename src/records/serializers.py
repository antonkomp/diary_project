from rest_framework import serializers
from .models import Entry


class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = ('id', 'date', 'header', 'text', 'image')


class CreateEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = ('header', 'text', 'image')


class UpdateEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = ('header', 'text', 'image', 'delete_image')


class DeleteEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = ('id', 'date', 'header', 'text', 'image')
