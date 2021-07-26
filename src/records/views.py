from django.shortcuts import render, redirect
from .forms import RecordForm
from .models import Record
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
from .serializers import RecordsSerializer, CreateRecordSerializer, UpdateRecordSerializer, DeleteRecordSerializer
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
def add_record(request):
    """Add records"""
    if request.method == 'POST':
        form = RecordForm(request.POST, request.FILES)
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
            return redirect('all_records')
        return JsonResponse({'success': False, })
    else:
        form = RecordForm()
        profile_image = Profile.objects.filter(user_id=request.user.id).first()
    return render(request, 'add_record.html', {'form': form, 'profile': profile_image})


@login_required
def all_records(request, page_number=1):
    if request.method == "GET":
        PageView.objects.get_or_create(url='records')
        entrance_url('records')
        search_query = request.GET.get('s', '')
        rec_user = Record.objects.filter(Q(user_id=request.user.id) & (Q(header__icontains=search_query) |
                   Q(text__icontains=search_query))) if search_query else Record.objects.filter(user_id=request.user.id)
        current_page = Paginator(rec_user, 25)
        quantity_records = 0
        for _ in rec_user:
            quantity_records += 1
        profile_image = Profile.objects.filter(user_id=request.user.id).first()
        return render(request, 'all_records.html', {'records': rec_user, 'quantity_records': quantity_records,
                                                    'keyword_search': search_query, 'profile': profile_image}) if search_query else render(
                    request, 'all_records.html', {'records': current_page.page(page_number),
                                                  'quantity_records': quantity_records, 'keyword_search': search_query, 'profile': profile_image})


@login_required
def detail_record(request, record_id):
    if request.method == "GET":
        record = Record.objects.filter(id=record_id).first()
        if record is None:
            messages.error(request, f'Entry {record_id} does not exist!')
            return redirect('all_records')
        if record.user_id != request.user.id:
            context = {'form': AuthenticationForm()}
            return render(request, 'login.html', context)
        profile_image = Profile.objects.filter(user_id=request.user.id).first()
        context = {'record': record, 'profile': profile_image}
        return render(request, 'detail_record.html', context)


@login_required
def edit_record(request, record_id):
    if request.method == "GET":
        record = Record.objects.filter(id=record_id).first()
        if record is None:
            messages.error(request, f'Entry {record_id} does not exist!')
            return redirect('all_records')
        if record.user_id != request.user.id:
            context = {'form': AuthenticationForm()}
            return render(request, 'login.html', context)
        record.delete_image = False
        profile_image = Profile.objects.filter(user_id=request.user.id).first()
        context = {'form': RecordForm(model_to_dict(record)), 'record': record, 'profile': profile_image}
        return render(request, 'edit_record.html', context)
    elif request.method == "POST":
        form = RecordForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            record = Record.objects.get(id=record_id)
            if request.is_ajax():
                record.header = request.POST.get('header')
                record.text = request.POST.get('text')
                record.voice_record = request.FILES.get('audio_data')
                record.image = request.FILES.get('image')
                record.delete_image = json.loads(request.POST.get('delete_image').lower())
            else:
                record.header = data['header']
                record.text = data['text']
                if data['image'] is not None:
                    record.image.delete()
                    record.image = data['image']
                record.delete_image = data['delete_image']
                if record.delete_image:
                    record.image.delete()
            record.check_edit = True
            record.save()
            messages.success(request, 'The entry details updated.')
            if request.is_ajax():
                return JsonResponse({'success': True, })
            return redirect('detail_record', record_id)
        return JsonResponse({'success': False, })


def delete_voice_record(request, record_id):
    """Delete voice record"""
    record = Record.objects.get(id=record_id)
    record.voice_record.delete()
    return JsonResponse({'success': True, })

@login_required
def delete_record(request, record_id):
    record = Record.objects.filter(id=record_id).first()
    if record.user_id != request.user.id:
        context = {'form': AuthenticationForm()}
        return render(request, 'login.html', context)
    if request.method == 'POST':
        record = Record.objects.filter(id=record_id).first()
        record.delete()
        messages.success(request, 'The entry deleted.')
        return redirect('all_records')


@login_required
def open_image(request, record_id):
    record = Record.objects.filter(id=record_id).first()
    if record.user_id != request.user.id:
        context = {'form': AuthenticationForm()}
        return render(request, 'login.html', context)
    context = {'record': record}
    return render(request, 'open_image.html', context)


@login_required
def send_record(request, record_id):
    record = Record.objects.filter(id=record_id).first()
    if record.user_id != request.user.id:
        context = {'form': AuthenticationForm()}
        return render(request, 'login.html', context)
    if request.method == 'POST':
        try:
            record = Record.objects.filter(id=record_id).first()
            user = User.objects.filter(id=request.user.id).first()

            subject, from_email, to = 'Sending your entry from Diary', 'antonkomp1@gmail.com', user.email
            html_content = loader.render_to_string('email/send_record.html', {'user': user, 'form': record}).strip()
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.content_subtype = 'html'
            msg.mixed_subtype = 'related'
            if record.image:
                image = MIMEImage(record.image.read())
                image.add_header('Content-ID', '<{}>'.format(record.image_filename))
                msg.attach(image)
            if record.voice_record:
                voice = MIMEAudio(record.voice_record.read())
                voice.add_header('Content-Disposition', 'attachment', filename=record.voice_filename)
                msg.attach(voice)
            msg.send()
            messages.success(request, 'The entry was successfully sent to email!')
        except smtplib.SMTPAuthenticationError:
            messages.error(request, 'Server side error! The record was not sent. '
                                    'Please inform the administrator about it.')
        return redirect('detail_record', record_id)


class APIRecords(generics.ListAPIView):
    queryset = Record.objects.all()
    serializer_class = RecordsSerializer

    def get_queryset(self):
        """Returns Records that belong to the current user"""
        try:
            return Record.objects.filter(user_id=self.request.user)
        except TypeError:
            pass


class APICreateRecord(generics.ListCreateAPIView):
    queryset = Record.objects.all()
    serializer_class = CreateRecordSerializer

    def get_queryset(self):
        """Returns Records that belong to the current user"""
        try:
            return Record.objects.filter(user_id=self.request.user)
        except TypeError:
            pass

    def perform_create(self, serializer):
        """The request user is set as author automatically."""
        try:
            serializer.save(user=self.request.user)
        except ValueError:
            pass


class APIUpdateRecord(generics.RetrieveUpdateAPIView):
    queryset = Record.objects.all()
    serializer_class = UpdateRecordSerializer

    def get_queryset(self):
        """Returns the record that needs to be updated"""
        try:
            return Record.objects.filter(user_id=self.request.user)
        except TypeError:
            pass


class APIDeleteRecord(generics.RetrieveDestroyAPIView):
    queryset = Record.objects.all()
    serializer_class = DeleteRecordSerializer

    def get_queryset(self):
        """Returns the record you want to delete"""
        try:
            return Record.objects.filter(user_id=self.request.user)
        except TypeError:
            pass
