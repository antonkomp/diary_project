from .models import Entry, Diary
from django import forms


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ('header', 'text', 'image', 'delete_image',)


class DiaryForm(forms.ModelForm):
    class Meta:
        model = Diary
        fields = ('name',)
