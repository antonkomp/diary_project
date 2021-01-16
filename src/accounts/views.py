from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrForm, ProfileForm, AccountKeyForm, MessagesForm
from django.template import loader
from django.core.mail import send_mail
from django.urls import reverse
from .models import ConfirmationKey, Profile, Account, Messages
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login, logout as logout_user
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .serializers import UserSerializer, UserEditSerializer, ProfileSerializer, ProfileEditSerializer, AccountSerializer
from rest_framework import generics
from django.contrib.auth.models import User


def main(request):
    if request.method == 'GET':
        return render(request, 'main.html')


def login_user(request):
    """
        Log a user in.
    """
    if request.method == 'GET':
        context = {'form': AuthenticationForm()}
        return render(request, 'login.html', context)
    elif request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if not form.is_valid():
            return HttpResponse('Your input is invalid', status=400)
        messages.success(request, f'Welcome!')
        login(request, form.get_user())
        return redirect('main')


@login_required
def logout(request):
    """
    Log a user out.
    """
    logout_user(request)
    messages.info(request, "You have successfully been logged out.")
    return redirect('main')


def registr_user(request):
    """
        Present a registration form for new users.
    """
    if request.method == 'GET':
        context = {'form': RegistrForm(), 'description': "Please fill in the form below to create your account."}
        return render(request, 'register.html', context)
    elif request.method == 'POST':
        form = RegistrForm(data=request.POST)
        if not form.is_valid():
            return HttpResponse('Your input is invalid', status=400)
        user = form.save(commit=False)
        user.email = form.cleaned_data['email']
        user.is_active = False
        user.save()
        key = ConfirmationKey(user=user)
        key.save()
        template = loader.render_to_string('email/register.txt', {
            'user': user,
            'url': request.build_absolute_uri(reverse('register_confirm', kwargs={'key': key.key}))
        })
        send_mail('Diary Registration', template, 'Diary <antonkomp1@gmail.com>', [user.email])
        messages.info(request,
                      "Please check the email address you provided for instructions on activating your account.")
        return redirect('main')


def register_confirm(request, key):
    """
    Confirms a user account.
    :param request:
    :param key: confirmation key to confirm registration
    """
    key = get_object_or_404(ConfirmationKey, key=key)
    key.user.is_active = True
    key.user.save()
    key.delete()
    messages.info(request, "Thank you! Your account has been activated.")
    return redirect('login')


@login_required
def profile(request):
    """
    Display a user's profile.
    """
    prof = Profile.objects.filter(user_id=request.user.id).first()
    return render(request, 'profile.html', {'profile': prof})


@login_required
def edit(request):
    prof = get_object_or_404(Profile, user=request.user.id)
    if request.method == 'POST':
        form = ProfileForm(instance=prof, data=request.POST)
        if form.is_valid():
            prof.user.first_name = form.cleaned_data['first_name']
            prof.user.last_name = form.cleaned_data['last_name']
            prof.user.email = form.cleaned_data['email']
            prof.user.save()
            form.save()
            messages.success(request, 'Profile was edited.')
            return redirect('profile')
    else:
        form = ProfileForm(
            instance=prof,
            initial={
                'first_name': prof.user.first_name,
                'last_name': prof.user.last_name,
                'email': prof.user.email,
            })
    return render(request, "edit.html", {'form': form})


@login_required
def account(request):
    if request.method == 'GET':
        acc = Account.objects.filter(profile_id=request.user.id).first()
        form = AccountKeyForm()
        context = {'account': acc, 'form': form}
        return render(request, 'account.html', context)
    if request.method == 'POST':
        form = AccountKeyForm(request.POST, request.FILES)
        if not form.is_valid():
            return HttpResponse('Your input is invalid', status=400)
        data = form.cleaned_data
        acc = Account.objects.get(profile_id=request.user.id)
        prof = Profile.objects.get(user_id=request.user.id)
        if data['key'] == 'kovrizhka':
            acc.key = data['key']
            acc.account_type = 'Premium'
            prof.account_type = 'Premium'
            messages.success(request, 'Congratulations, you have switched to a Premium account!')
        elif data['key'] == 'backtoschool':
            acc.key = data['key']
            acc.account_type = 'Standard'
            prof.account_type = 'Standard'
            messages.success(request, 'You have switched to a Standard account!')
        else:
            messages.warning(request, 'The wrong key was entered!')
        acc.save()
        prof.save()
        return redirect('account')


@login_required
def message(request):
    """
    Show user messages.
    """
    mess = Messages.objects.filter(user_id=request.user.id).first()
    return render(request, 'messages.html', {'messages': mess})


@login_required
def detail_message(request, message_id):
    if request.method == "GET":
        mess = Messages.objects.filter(id=message_id).first()
        if mess.user_id != request.user.id:
            context = {'form': AuthenticationForm()}
            return render(request, 'login.html', context)
        context = {'message': mess}
        return render(request, 'detail_message.html', context)


@login_required
def send_message(request):
    """
    Send message
    """
    if request.method == 'POST':
        form = MessagesForm(request.POST, request.FILES)
        if form.is_valid():
            us = form.save(commit=False)
            us.user = request.user
            us.save()
            messages.success(request, 'New message was sent!')
            return redirect('messages')
    else:
        form = MessagesForm()
    return render(request, 'send_message.html', {'form': form})


@login_required
def open_image_message(request, message_id):
    mess = Messages.objects.filter(id=message_id).first()
    if mess.user_id != request.user.id:
        context = {'form': AuthenticationForm()}
        return render(request, 'login.html', context)
    context = {'message': mess}
    return render(request, 'open_image_message.html', context)


@login_required
def delete_message(request, message_id):
    mess = Messages.objects.filter(id=message_id).first()
    if mess.user_id != request.user.id:
        context = {'form': AuthenticationForm()}
        return render(request, 'login.html', context)
    if request.method == 'POST':
        mess = Messages.objects.filter(id=message_id).first()
        mess.delete()
        messages.success(request, 'Message was deleted.')
        return redirect('messages')


@login_required
def api(request):
    return render(request, 'API.html')


class APIUser(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            obj = queryset.get(pk=self.request.user.id)
            self.check_object_permissions(self.request, obj)
            return obj
        except User.DoesNotExist:
            pass


class APIUserEdit(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserEditSerializer

    def get_object(self):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            obj = queryset.get(pk=self.request.user.id)
            self.check_object_permissions(self.request, obj)
            return obj
        except User.DoesNotExist:
            pass


class APIProfile(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_object(self):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            obj = queryset.get(pk=self.request.user.id)
            self.check_object_permissions(self.request, obj)
            return obj
        except Profile.DoesNotExist:
            pass


class APIProfileEdit(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileEditSerializer

    def get_object(self):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            obj = queryset.get(pk=self.request.user.id)
            self.check_object_permissions(self.request, obj)
            return obj
        except Profile.DoesNotExist:
            pass


class APIAccount(generics.RetrieveAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_object(self):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            obj = queryset.get(pk=self.request.user.id)
            self.check_object_permissions(self.request, obj)
            return obj
        except Account.DoesNotExist:
            pass
