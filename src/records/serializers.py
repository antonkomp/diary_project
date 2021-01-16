from rest_framework import serializers
from .models import Record


class RecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = ('id', 'date', 'heading', 'text', 'image')


class CreateRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = ('heading', 'text', 'image')


class UpdateRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = ('heading', 'text', 'image', 'delete_image')


class DeleteRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = ('id', 'date', 'heading', 'text', 'image')
