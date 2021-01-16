from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
import os


class Record(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now=True)
    heading = models.CharField(max_length=70, default='no_theme')
    text = models.TextField(max_length=9999)
    image = models.ImageField(blank=True, null=True)
    delete_image = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.heading} ({self.user}) - {str(self.date)[:19]}   {str(self.image)[-19:]}'

    class Meta:
        ordering = ('-date', '-user',)

    @property
    def image_filename(self):
        return os.path.basename(self.image.name)


@receiver(pre_delete, sender=Record)
def record_delete(sender, instance, **kwargs):
    instance.image.delete(False)
