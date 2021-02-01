from django.contrib import admin
from .models import ConfirmationKey, Profile, Messages

admin.site.register(ConfirmationKey)
admin.site.register(Profile)
admin.site.register(Messages)
