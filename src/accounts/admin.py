from django.contrib import admin
from .models import ConfirmationKey, Profile, Messages, PageView

admin.site.register(ConfirmationKey)
admin.site.register(Profile)
admin.site.register(Messages)
admin.site.register(PageView)