from django.shortcuts import render, redirect
from .forms import EntryForm, DiaryForm
from .models import Entry, Diary
from accounts.models import PageView, Profile
from django.forms import model_to_dict
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.core.mail import EmailMessage
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from .serializers import EntrySerializer, CreateEntrySerializer, UpdateEntrySerializer, DeleteEntrySerializer
from rest_framework import generics
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import F, Q
from PIL import Image, UnidentifiedImageError
import io
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json


MAX_SIZE = 1024

SUCCESS_MESSAGE = 'New entry added!'
SUCCESS_VOICE_MESSAGE = 'New entry with voice record added!'


def entrance_url(url):
    entrance = PageView.objects.filter(url=url)
    entrance.update(views=F('views') + 1)


def resize_image(us):
    if us.image.width <= MAX_SIZE and us.image.height <= MAX_SIZE:
        return

    try:
        with Image.open(us.image) as img:
            img.thumbnail((MAX_SIZE, MAX_SIZE), Image.ANTIALIAS)
            thumb_io = io.BytesIO()
            img.save(thumb_io, format=img.format, quality=86)

            if img.size != us.image.size:
                us.image.save(us.image.name, ContentFile(thumb_io.getvalue()), save=False)
    except UnidentifiedImageError:
        pass


@login_required
def add_entry(request):
    """Add entry"""
    if request.method == 'POST':
        form = EntryForm(request.POST, request.FILES)
        if form.is_valid():
            us = form.save(commit=False)
            us.user = request.user
            if request.is_ajax():
                us.header = request.POST.get('header')
                us.text = request.POST.get('text')
                us.voice_record = request.FILES.get('audio_data')
                us.image = request.FILES.get('image')
                us.delete_image = json.loads(request.POST.get('delete_image').lower())
                messages.success(request, 'New entry with voice record added!')

            if us.image.name is not None and us.delete_image:
                us.image = ''
            elif us.image.name is not None and us.delete_image is False and us.header != '!original!':
                resize_image(us)

            us.save()
            if request.is_ajax():
                return JsonResponse({'success': True, })

            messages.success(request, 'New entry added!')
            return redirect('all_entries')

        return JsonResponse({'success': False, })
    else:
        form = EntryForm()
        profile_image = Profile.objects.filter(user_id=request.user.id).first()
        return render(request, 'add_entry.html', {'form': form, 'profile': profile_image})


def handle_ajax_request():
    return JsonResponse({'success': True})


@login_required
def create_new_diary(request):
    """Create new diary"""
    if request.method == 'POST':
        form = DiaryForm(request.POST)
        if form.is_valid():
            us = form.save(commit=False)
            us.user = request.user
            us.save()
            messages.success(request, 'New diary created!')
            return redirect('my_public_diaries')
    else:
        form = DiaryForm()
        profile_image = get_object_or_404(Profile, user_id=request.user.id)
        context = {'form': form, 'profile': profile_image}
        return render(request, 'create_new_diary.html', context)


@login_required
def all_public_diaries(request):
    context = {}
    return render(request, 'all_public_diaries.html', context)


@login_required
def my_public_diaries(request):
    if request.method == "GET":
        profile_image = get_object_or_404(Profile, user_id=request.user.id)
        diaries_user = Diary.objects.filter(user_id=request.user.id).select_related('user')

        context = {'profile': profile_image, 'diaries': diaries_user}
        return render(request, 'my_public_diaries.html', context)


@login_required
def all_entries(request, page_number=1):
    if request.method == "GET":
        PageView.objects.get_or_create(url='entries')
        entrance_url('entries')
        search_query = request.GET.get('s', '')
        rec_user = Entry.objects.filter(
            Q(user_id=request.user.id) & (Q(header__icontains=search_query) | Q(text__icontains=search_query))
        )
        quantity_entries = rec_user.count()

        current_page = Paginator(rec_user, 25)

        profile_image = get_object_or_404(Profile, user_id=request.user.id)
        context = {
            'quantity_entries': quantity_entries,
            'keyword_search': search_query,
            'profile': profile_image
        }
        if search_query:
            context['entries'] = rec_user
        else:
            context['entries'] = current_page.page(page_number)

        return render(request, 'all_entries.html', context)


@login_required
def detail_entry(request, entry_id):
    try:
        entry = Entry.objects.get(id=entry_id, user=request.user)
    except Entry.DoesNotExist:
        messages.error(request, f'Entry {entry_id} does not exist!')
        return redirect('all_entries')

    context = {'entry': entry, 'profile': Profile.objects.filter(user=request.user).first()}
    return render(request, 'detail_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)
    if request.method == "GET":
        if entry.user_id != request.user.id:
            context = {'form': AuthenticationForm()}
            return render(request, 'login.html', context)

        entry.delete_image = False
        profile_image = Profile.objects.filter(user_id=request.user.id).first()
        context = {'form': EntryForm(model_to_dict(entry)), 'entry': entry, 'profile': profile_image}
        return render(request, 'edit_entry.html', context)
    elif request.method == "POST":
        form = EntryForm(request.POST, request.FILES)
        if form.is_valid():
            if request.is_ajax():
                entry.header = request.POST.get('header')
                entry.text = request.POST.get('text')
                entry.voice_record = request.FILES.get('audio_data')
                entry.image = request.FILES.get('image')
                entry.delete_image = json.loads(request.POST.get('delete_image', 'false').lower())
            else:
                data = form.cleaned_data
                entry.header = data['header']
                entry.text = data['text']
                entry.image = request.FILES.get('image', entry.image)
                entry.delete_image = data.get('delete_image', False)
                if entry.delete_image:
                    entry.image.delete()

            entry.check_edit = True
            entry.save()
            messages.success(request, 'The entry details updated.')
            success = True
            if request.is_ajax():
                return JsonResponse({'success': success})

            return redirect('detail_entry', entry_id)

        success = False
        if request.is_ajax():
            return JsonResponse({'success': success})

        return render(request, 'edit_entry.html', {'form': form, 'entry': entry})


def delete_voice_record(entry_id):
    """Delete voice record"""
    entry = get_object_or_404(Entry, id=entry_id)
    entry.voice_record.delete()
    return {'success': True}


@login_required
def delete_entry(request, entry_id):
    entry = Entry.objects.filter(id=entry_id, user_id=request.user.id).first()
    if not entry:
        context = {'form': AuthenticationForm()}
        return render(request, 'login.html', context)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'The entry deleted.')
        return redirect('all_entries')


@login_required
def open_image(request, entry_id):
    entry = Entry.objects.filter(id=entry_id, user=request.user).first()
    if not entry:
        return render(request, 'login.html', {'form': AuthenticationForm()})
    return render(request, 'open_image.html', {'entry': entry})

import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import Entry

@require_http_methods(["POST"])
def send_entry(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id, user=request.user)
    user = request.user

    subject = 'Sending your entry from Diary'
    from_email = 'antonkomp1@gmail.com'
    to = user.email

    html_content = render_to_string('email/send_entry.html', {'user': user, 'form': entry})
    print(html_content)

    url = 'https://www.googleapis.com/gmail/v1/users/me/messages/send?key=' + 'AIzaSyBCJMCzBf4IwmwyyMBDd3yQ_CX3cN7lfSs' # settings.GOOGLE_API_KEY

    message = {'raw': base64.urlsafe_b64encode(html_content.encode('utf-8')).decode('utf-8')}

    body = {'raw': base64.urlsafe_b64encode(html_content.encode('utf-8')).decode('utf-8')}
    print(body)

    headers = {
        'Authorization': 'Bearer ' + 'AIzaSyBCJMCzBf4IwmwyyMBDd3yQ_CX3cN7lfSs', # settings.GOOGLE_API_KEY,
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, json=body)
    print(response.text)

    if response.status_code == 200:
        messages.success(request, 'The entry was successfully sent to email!')
    else:
        messages.error(request, 'An error occurred while sending the email.')

    return HttpResponseRedirect(reverse('detail_entry', args=[entry_id]))

# @login_required
# @require_http_methods(["POST"])
# def send_entry(request, entry_id):
#     entry = get_object_or_404(Entry, id=entry_id, user=request.user)
#     user = request.user
#
#     subject = 'Sending your entry from Diary'
#     from_email = 'antonkomp1@gmail.com'
#     to = user.email
#
#     html_content = render_to_string('email/send_entry.html', {'user': user, 'form': entry})
#
#     email = EmailMessage(subject, html_content, from_email, [to])
#     if entry.image:
#         email.attach_file(entry.image.path)
#     if entry.voice_record:
#         email.attach_file(entry.voice_record.path)
#
#     email.send(fail_silently=False)
#
#     messages.success(request, 'The entry was successfully sent to email!')
#     return HttpResponseRedirect(reverse('detail_entry', args=[entry_id]))

# temp !!!!!
import base64
# import os.path
# from email.mime.text import MIMEText
# from google.oauth2.credentials import Credentials
# from googleapiclient.discovery import build
# from django.shortcuts import redirect
# from django.conf import settings
#
# @require_http_methods(["POST"])
# def send_entry(request, entry_id):
#     entry = get_object_or_404(Entry, id=entry_id, user=request.user)
#     user = request.user
#
#     subject = 'Sending your entry from Diary'
#     from_email = 'antonkomp1@gmail.com'
#     to = user.email
#
#     html_content = render_to_string('email/send_entry.html', {'user': user, 'form': entry})
#
#     credentials_file = os.path.join(os.path.dirname(__file__), 'google_console_creds.json')
#     print(credentials_file, '!!!!')
#     credentials = Credentials.from_authorized_user_file(credentials_file)
#     print(credentials, '!!!!')
#     # api_key = 'AIzaSyBCJMCzBf4IwmwyyMBDd3yQ_CX3cN7lfSs'
#     if not credentials:
#         flow = InstalledAppFlow.from_client_secrets_file(str(settings.GOOGLE_OAUTH2_CLIENT_SECRETS_FILE), SCOPES)
#         credentials = flow.run_local_server(port=0)
#
#     # if credentials and credentials.expired and credentials.refresh_token:
#     #     credentials.refresh(Credentials())
#
#     service = build('gmail', 'v1', credentials=credentials)
#     message = MIMEText(html_content, 'html')
#     message['to'] = to
#     message['subject'] = subject
#     create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
#     send_message = service.users().messages().send(userId='me', body=create_message).execute()
#
#     messages.success(request, 'The entry was successfully sent to email!')
#     return HttpResponseRedirect(reverse('detail_entry', args=[entry_id]))


# import base64
# from email.mime.text import MIMEText
# from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from django.shortcuts import redirect
#
# # Здесь необходимо указать Client ID и Client Secret, которые были получены на предыдущих шагах.
# CLIENT_ID = '248664437485-grkrj1jut62qbube7h20mhnc3sva7gp6.apps.googleusercontent.com>'
# CLIENT_SECRET = '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'
# REDIRECT_URI = 'http://localhost:8000/oauth2callback'
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
#
#
# def get_credentials(request):
#     flow = InstalledAppFlow.from_client_secrets_file(
#         'google_console_creds.json',
#         scopes=SCOPES,
#         redirect_uri=REDIRECT_URI
#     )
#
#     if 'code' not in request.GET:
#         auth_url, _ = flow.authorization_url(prompt='consent')
#         return redirect(auth_url)
#
#     flow.fetch_token(code=request.GET['code'])
#     credentials = flow.credentials
#     return credentials
#
#
# def send_email(request):
#     credentials = get_credentials(request)
#
#     service = build('gmail', 'v1', credentials=credentials)
#     message = MIMEText(request.POST['message'], 'html')
#     message['to'] = request.POST['to']
#     message['subject'] = request.POST['subject']
#     create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
#     send_message = (service.users().messages().send(userId='me', body=create_message).execute())
#     print(F'sent message to {message["to"]} Message Id: {send_message["id"]}')
#     return redirect('home')


class APIEntries(generics.ListAPIView):
    queryset = Entry.objects.all()
    serializer_class = EntrySerializer

    def get_queryset(self):
        """Returns entries that belong to the current user"""
        try:
            return Entry.objects.filter(user_id=self.request.user)
        except TypeError:
            pass


class APICreateEntry(generics.ListCreateAPIView):
    queryset = Entry.objects.all()
    serializer_class = CreateEntrySerializer

    def get_queryset(self):
        """Returns Entries that belong to the current user"""
        try:
            return Entry.objects.filter(user_id=self.request.user)
        except TypeError:
            pass

    def perform_create(self, serializer):
        """The request user is set as author automatically."""
        try:
            serializer.save(user=self.request.user)
        except ValueError:
            pass


class APIUpdateEntry(generics.RetrieveUpdateAPIView):
    queryset = Entry.objects.all()
    serializer_class = UpdateEntrySerializer

    def get_queryset(self):
        """Returns the entry that needs to be updated"""
        try:
            return Entry.objects.filter(user_id=self.request.user)
        except TypeError:
            pass


class APIDeleteEntry(generics.RetrieveDestroyAPIView):
    queryset = Entry.objects.all()
    serializer_class = DeleteEntrySerializer

    def get_queryset(self):
        """Returns the entry you want to delete"""
        try:
            return Entry.objects.filter(user_id=self.request.user)
        except TypeError:
            pass
