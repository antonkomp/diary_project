from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete


class Chat(models.Model):
    members = models.ManyToManyField(User, verbose_name='Members')
    last_message = models.ForeignKey(
        'Message',
        related_name="last_message",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )


class Message(models.Model):
    """
    Sending message to another user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='User')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, verbose_name='Chat')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    text = models.TextField(max_length=9999, verbose_name='Message')
    is_readed = models.BooleanField(default=False, verbose_name='Readed')

    class Meta:
        ordering = ('date',)

    def __str__(self):
        return self.text
