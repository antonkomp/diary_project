from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrForm, ProfileForm, AccountKeyForm, MessagesForm
from django.template import loader
from django.core.mail import send_mail
from django.urls import reverse
from .models import ConfirmationKey, Profile, Account, Messages, PageView
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import login, logout as logout_user
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .serializers import UserSerializer, UserEditSerializer, ProfileSerializer, ProfileEditSerializer, AccountSerializer
from rest_framework import generics
from django.contrib.auth.models import User
from django.db.models import F, Q
from PIL import Image
import io
from django.core.files.base import ContentFile
from django.http import JsonResponse


MAX_SIZE = 300


def csrf_failure(request, reason=""):
    ctx = {'message': ' Error 403. This user is already logged in!'}
    return render(request, '403.html', ctx)


def entrance_url(url):
    entrance = PageView.objects.filter(url=url)
    entrance.update(views=F('views') + 1)


def main(request):
    if request.method == 'GET':
        PageView.objects.get_or_create(url='main')
        entrance_url('main')
        profile_image = Profile.objects.filter(user_id=request.user.id).first()
        return render(request, 'main.html', {'profile': profile_image})


def login_user(request):
    """
        Log a user in.
    """
    if request.method == 'GET':
        logout_user(request)
        context = {'form': AuthenticationForm()}
        return render(request, 'login.html', context)
    elif request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if not form.is_valid():
            messages.error(request, 'Your input is invalid!')
            return redirect('login')
        messages.success(request, 'Welcome!')
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
        logout_user(request)
        context = {'form': RegistrForm(), 'description': "Please fill in the form below to create your account."}
        return render(request, 'register.html', context)
    elif request.method == 'POST':
        form = RegistrForm(data=request.POST)
        if not form.is_valid():
            messages.error(request, 'Your input is invalid!')
            return redirect('register')
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


def validate_username(request):
    """Check username availability"""
    username = request.GET.get('username', None)
    response = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(response)


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
    PageView.objects.get_or_create(url='profile')
    entrance_url('profile')
    prof = Profile.objects.filter(user_id=request.user.id).first()
    return render(request, 'profile.html', {'profile': prof})


def upload_avatar(prof, prof_old):
    if prof.image.width > MAX_SIZE or prof.image.height > MAX_SIZE:
        img = Image.open(prof.image)
        img.thumbnail((MAX_SIZE, MAX_SIZE), Image.ANTIALIAS)
        thumb_io = io.BytesIO()
        img.save(thumb_io, img.format, quality=90)
        prof.image.save(prof.image.name, ContentFile(thumb_io.getvalue()), save=False)
    prof_old.image = prof.image


@login_required
def edit(request):
    prof = get_object_or_404(Profile, user=request.user.id)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=prof)
        if form.is_valid():
            prof_old = Profile.objects.get(user_id=request.user.id)
            prof.user.first_name = form.cleaned_data['first_name']
            prof.user.last_name = form.cleaned_data['last_name']
            prof.user.email = form.cleaned_data['email']
            if prof.image.name != prof_old.image.name:
                if prof.image.name == '' and prof_old.image.name != '':
                    prof_old.image.delete()
                elif prof.image.name != '' and prof_old.image.name != '':
                    prof_old.image.delete()
                    upload_avatar(prof, prof_old)
                else:
                    upload_avatar(prof, prof_old)
            prof.user.save()
            form.save()
            messages.success(request, 'Profile edited.')
            return redirect('profile')
    else:
        form = ProfileForm(
            instance=prof,
            initial={
                'first_name': prof.user.first_name,
                'last_name': prof.user.last_name,
                'email': prof.user.email,
            })
        profile_image = Profile.objects.filter(user_id=request.user.id).first()
        return render(request, "edit.html", {'form': form, 'profile': profile_image})


@login_required
def account(request):
    if request.method == 'GET':
        PageView.objects.get_or_create(url='account')
        entrance_url('account')
        acc = Account.objects.filter(profile_id=request.user.id).first()
        form = AccountKeyForm()
        profile_image = Profile.objects.filter(user_id=request.user.id).first()
        context = {'account': acc, 'form': form, 'profile': profile_image}
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
    PageView.objects.get_or_create(url='message')
    entrance_url('message')
    search_query = request.GET.get('s', '')
    profile_image = Profile.objects.filter(user_id=request.user.id).first()
    if search_query:
        mess = Messages.objects.filter(Q(recipient=request.user) & (Q(header__icontains=search_query) |
                                                                    Q(text__icontains=search_query) |
                                                                    Q(sender__icontains=search_query)))
    else:
        mess = Messages.objects.filter(recipient=request.user)
    return render(request, 'messages.html', {'form_mess': mess, 'keyword_search': search_query, 'profile': profile_image})


@login_required
def message_details(request, messages_id):
    if request.method == "GET":
        mess = Messages.objects.filter(id=messages_id).first()
        if mess.recipient != str(request.user):
            context = {'form': AuthenticationForm()}
            return render(request, 'login.html', context)
        profile_image = Profile.objects.filter(user_id=request.user.id).first()
        context = {'message': mess, 'profile': profile_image}
        return render(request, 'detail_message.html', context)


@login_required
def send_message(request):
    """
    Send message
    """
    if request.method == 'POST':
        form = MessagesForm(request.POST, request.FILES)
        if form.is_valid():
            mess_form = form.save(commit=False)
            mess_form.user = request.user
            mess_form.sender = request.user
            if str(mess_form.image) != '' and mess_form.delete_image:
                mess_form.image = ''
            checking = User.objects.filter(username=mess_form.recipient).first()
            if checking is None:
                messages.error(request, 'This user does not exist!')
                form = MessagesForm(initial={
                    'header': mess_form.header,
                    'text': mess_form.text,
                })
                return render(request, 'send_message.html', {'form': form})
            mess_form.save()
            messages.success(request, 'New message sent!')
            return redirect('my_messages')
    else:
        form = MessagesForm()
        profile_image = Profile.objects.filter(user_id=request.user.id).first()
    return render(request, 'send_message.html', {'form': form, 'profile': profile_image})


@login_required
def open_image_message(request, message_id):
    mess = Messages.objects.filter(id=message_id).first()
    if mess.recipient != str(request.user):
        context = {'form': AuthenticationForm()}
        return render(request, 'login.html', context)
    context = {'message': mess}
    return render(request, 'open_image_message.html', context)


@login_required
def delete_message(request, message_id):
    mess = Messages.objects.filter(id=message_id).first()
    if mess.recipient != str(request.user):
        context = {'form': AuthenticationForm()}
        return render(request, 'login.html', context)
    if request.method == 'POST':
        mess = Messages.objects.filter(id=message_id).first()
        mess.delete()
        messages.success(request, 'Message deleted.')
        return redirect('my_messages')


@login_required
def api(request):
    PageView.objects.get_or_create(url='api')
    entrance_url('api')
    profile_image = Profile.objects.filter(user_id=request.user.id).first()
    return render(request, 'API.html', {'profile': profile_image})


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
