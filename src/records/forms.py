from .models import Record, Diary
from django import forms


class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ('header', 'text', 'image', 'delete_image',)


class DiaryForm(forms.ModelForm):
    class Meta:
        model = Diary
        fields = ('name',)
