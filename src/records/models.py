from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
import os


class Record(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now=True)
    header = models.CharField(max_length=70, default='no_theme')
    text = models.TextField(max_length=9999, blank=True, null=True)
    image = models.ImageField(upload_to='image_entries/', blank=True, null=True)
    delete_image = models.BooleanField(default=False)
    voice_record = models.FileField(upload_to='voice_record/', blank=True, null=True)

    def __str__(self):
        return f'{self.header} ({self.user}) - {str(self.date)[:19]}   {"📷" if self.image else " "}' \
               f' {"🎵" if self.voice_record else " "}'

    class Meta:
        ordering = ('-date', '-user',)

    @property
    def image_filename(self):
        return os.path.basename(self.image.name)

    @property
    def voice_filename(self):
        return os.path.basename(self.voice_record.name)


@receiver(pre_delete, sender=Record)
def image_entry_delete(sender, instance, **kwargs):
    instance.image.delete(False)


@receiver(pre_delete, sender=Record)
def voice_record_entry_delete(sender, instance, **kwargs):
    instance.voice_record.delete(False)
