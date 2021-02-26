from django.db import models
from django.contrib.auth.models import User
from .utils import uuid
from django.dispatch import receiver
from django.utils.timezone import now
from django.db.models.signals import pre_delete, post_save


class Profile(models.Model):
    """
    Information about an author.
    """
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=15, default='Standard')
    birthday = models.DateField(blank=True, null=True,
                                help_text="Birthday in YYYY-MM-DD format [used for displaying age].")
    location = models.CharField(max_length=40, blank=True, help_text="Geographic location.")
    website = models.URLField(blank=True, help_text="A personal blog or website.")
    bio = models.TextField(blank=True, help_text="A brief biography.")
    image = models.ImageField(upload_to='avatar/', blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.get_username()

    def age(self):
        """
        Calculate the age of the user.
        """
        if not self.birthday:
            return None
        n, b = now().date(), self.birthday
        return n.year - b.year - (0 if n.month > b.month or n.month == b.month and n.day >= b.day else 1)

    class Meta:
        ordering = ('-user__last_login',)


@receiver(pre_delete, sender=Profile)
def record_delete(sender, instance, **kwargs):
    instance.image.delete(False)


@receiver(post_save, sender=User)
def create_profile(instance, created, **kwargs):
    """
    Create a profile whenever a user is created.
    """
    if created:
        Profile.objects.create(user=instance)


class Account(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=15, default='Standard')
    key = models.CharField(max_length=20, blank=True, null=True)


@receiver(models.signals.post_save, sender=Profile)
def create_account(instance, created, **kwargs):
    """
    Create an account whenever a profile is created.
    """
    if created:
        Account.objects.create(profile=instance)


class ConfirmationKey(models.Model):
    """
    Unique token for confirming a user account or resetting a password.
    """
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    key = models.CharField(max_length=32, default=uuid)


class Messages(models.Model):
    """
    Sending message to another user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(auto_now=True)
    recipient = models.CharField(max_length=150)
    sender = models.CharField(max_length=150, null=True, blank=True)
    heading = models.CharField(max_length=70, null=True, blank=True)
    text = models.TextField(max_length=9999)
    image = models.ImageField(blank=True, null=True)
    delete_image = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} > ({self.recipient}) - {str(self.date)[:19]} {str(self.image)[-19:]}'

    class Meta:
        ordering = ('-date',)


class PageView(models.Model):
    url = models.CharField(max_length=70, blank=True, null=True, unique=True)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.url} - {self.views}'

