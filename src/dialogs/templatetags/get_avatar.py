from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def get_avatar(user):
    if user.profile.image:
        return mark_safe('<img class="avatar_message" src="{{ message.user.profile.image.url }}" alt="user_image" width="38" height="38" style="border-radius: 50%; border: 2px solid #e6e6e6;" title="">')
    else:
        return mark_safe('<img class="image_default" src="{% static "image/anonymous.jpg" %}" alt="user_image" width="38" height="38" style="border-radius: 50%" title="">')
