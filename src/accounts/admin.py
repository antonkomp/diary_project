from django.contrib import admin
from .models import ConfirmationKey, Profile, PageView

admin.site.register(ConfirmationKey)
admin.site.register(Profile)
admin.site.register(PageView)
