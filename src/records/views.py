from django.shortcuts import render, redirect
from .forms import EntryForm, DiaryForm
from .models import Entry, Diary
from accounts.models import PageView, Profile
from django.forms import model_to_dict
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
import smtplib
from .serializers import EntrySerializer, CreateEntrySerializer, UpdateEntrySerializer, DeleteEntrySerializer
from rest_framework import generics
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import F, Q
from PIL import Image
import io
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.http import JsonResponse
import json


MAX_SIZE = 1024


def entrance_url(url):
    entrance = PageView.objects.filter(url=url)
    entrance.update(views=F('views') + 1)


def resize_image(us):
    if us.image.width > MAX_SIZE or us.image.height > MAX_SIZE:
        with Image.open(us.image) as img:
            img.thumbnail((MAX_SIZE, MAX_SIZE), Image.ANTIALIAS)
            thumb_io = io.BytesIO()
            img.save(thumb_io, img.format, quality=86)
            us.image.save(us.image.name, ContentFile(thumb_io.getvalue()), save=False)


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
        profile_image = Profile.objects.filter(user_id=request.user.id).first()
        context = {'form': form, 'profile': profile_image}
        return render(request, 'create_new_diary.html', context)


@login_required
def all_public_diaries(request):
    context = {}
    return render(request, 'all_public_diaries.html', context)


@login_required
def my_public_diaries(request):
    if request.method == "GET":
        diaries_user = Diary.objects.filter(user_id=request.user.id)

        profile_image = Profile.objects.filter(user_id=request.user.id).first()
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
        ) if search_query else Entry.objects.filter(user_id=request.user.id)

        current_page = Paginator(rec_user, 25)
        quantity_entries = 0
        for _ in rec_user:
            quantity_entries += 1

        profile_image = Profile.objects.filter(user_id=request.user.id).first()
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
    if request.method == "GET":
        entry = Entry.objects.filter(id=entry_id).first()
        if entry is None:
            messages.error(request, f'Entry {entry_id} does not exist!')
            return redirect('all_entries')
        if entry.user_id != request.user.id:
            context = {'form': AuthenticationForm()}
            return render(request, 'login.html', context)
        profile_image = Profile.objects.filter(user_id=request.user.id).first()
        context = {'entry': entry, 'profile': profile_image}
        return render(request, 'detail_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    if request.method == "GET":
        entry = Entry.objects.filter(id=entry_id).first()
        if entry is None:
            messages.error(request, f'Entry {entry_id} does not exist!')
            return redirect('all_entries')
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
            data = form.cleaned_data
            entry = Entry.objects.get(id=entry_id)
            if request.is_ajax():
                entry.header = request.POST.get('header')
                entry.text = request.POST.get('text')
                entry.voice_record = request.FILES.get('audio_data')
                entry.image = request.FILES.get('image')
                entry.delete_image = json.loads(request.POST.get('delete_image').lower())
            else:
                entry.header = data['header']
                entry.text = data['text']
                if data['image'] is not None:
                    entry.image.delete()
                    entry.image = data['image']
                entry.delete_image = data['delete_image']
                if entry.delete_image:
                    entry.image.delete()
            entry.check_edit = True
            entry.save()
            messages.success(request, 'The entry details updated.')
            if request.is_ajax():
                return JsonResponse({'success': True, })
            return redirect('detail_entry', entry_id)
        return JsonResponse({'success': False, })


def delete_voice_record(entry_id):
    """Delete voice record"""
    entry = Entry.objects.get(id=entry_id)
    entry.voice_record.delete()
    return JsonResponse({'success': True, })


@login_required
def delete_entry(request, entry_id):
    entry = Entry.objects.filter(id=entry_id).first()
    if entry.user_id != request.user.id:
        context = {'form': AuthenticationForm()}
        return render(request, 'login.html', context)
    if request.method == 'POST':
        entry = Entry.objects.filter(id=entry_id).first()
        entry.delete()
        messages.success(request, 'The entry deleted.')
        return redirect('all_entries')


@login_required
def open_image(request, entry_id):
    entry = Entry.objects.filter(id=entry_id).first()
    if entry.user_id != request.user.id:
        context = {'form': AuthenticationForm()}
        return render(request, 'login.html', context)
    context = {'entry': entry}
    return render(request, 'open_image.html', context)


@login_required
def send_entry(request, entry_id):
    entry = Entry.objects.filter(id=entry_id).first()
    if entry.user_id != request.user.id:
        context = {'form': AuthenticationForm()}
        return render(request, 'login.html', context)
    if request.method == 'POST':
        try:
            entry = Entry.objects.filter(id=entry_id).first()
            user = User.objects.filter(id=request.user.id).first()

            subject, from_email, to = 'Sending your entry from Diary', 'antonkomp1@gmail.com', user.email
            html_content = loader.render_to_string('email/send_entry.html', {'user': user, 'form': entry}).strip()
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.content_subtype = 'html'
            msg.mixed_subtype = 'related'
            if entry.image:
                image = MIMEImage(entry.image.read())
                image.add_header('Content-ID', '<{}>'.format(entry.image_filename))
                msg.attach(image)
            if entry.voice_record:
                voice = MIMEAudio(entry.voice_record.read())
                voice.add_header('Content-Disposition', 'attachment', filename=entry.voice_filename)
                msg.attach(voice)
            msg.send()
            messages.success(request, 'The entry was successfully sent to email!')
        except smtplib.SMTPAuthenticationError:
            messages.error(request, 'Server side error! The entry was not sent. '
                                    'Please inform the administrator about it.')
        return redirect('detail_entry', entry_id)


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
