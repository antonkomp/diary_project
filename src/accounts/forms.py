from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Account, Messages


class RegistrForm(UserCreationForm):
    """
    Form for new user registrations.
    """
    email = forms.EmailField(required=True, max_length=250, help_text="Used for account verification "
                                                                      "and password resets.")


class AccountKeyForm(forms.ModelForm):
    """
    Form for entering the key and switching to a premium account.
    """
    class Meta:
        model = Account
        fields = ('key',)


class ProfileForm(forms.ModelForm):
    """
    Form for editing a user's profile.
    """
    first_name = forms.CharField(
        max_length=30,
        required=False,
        help_text="First name [optional].",
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        help_text="Last name [optional].",
    )
    email = forms.EmailField(help_text="Used for account verification and password resets.")

    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'email', 'birthday', 'location', 'website', 'bio', 'image')


class MessagesForm(forms.ModelForm):
    """
    Form for sending messages to other users.
    """
    class Meta:
        model = Messages
        fields = ('recipient', 'sender', 'header', 'text', 'image', 'delete_image')
