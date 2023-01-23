from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete


class Chat(models.Model):
    members = models.ManyToManyField(User)
    slug = models.SlugField(unique=True)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    text = models.TextField(max_length=9999)
    is_readed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} - {str(self.date)[:19]}'

    class Meta:
        ordering = ('-date',)



