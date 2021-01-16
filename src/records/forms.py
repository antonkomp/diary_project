from .models import Record
from django import forms


class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ('heading', 'text', 'image', 'delete_image')
