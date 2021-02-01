from django.shortcuts import render, redirect
from .forms import RecordForm
from .models import Record
from django.forms import model_to_dict
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
import smtplib
from .serializers import RecordsSerializer, CreateRecordSerializer, UpdateRecordSerializer, DeleteRecordSerializer
from rest_framework import generics
from django.contrib.auth.forms import AuthenticationForm


@login_required
def add_record(request):
    """Add records"""
    if request.method == 'POST':
        form = RecordForm(request.POST, request.FILES)
        if form.is_valid():
            us = form.save(commit=False)
            us.user = request.user
            if str(us.image) != '' and us.delete_image:
                us.image = ''
            us.save()
            messages.success(request, 'New entry added!')
            return redirect('all_records')
    else:
        form = RecordForm()
    return render(request, 'add_record.html', {'form': form})


@login_required
def all_records(request):
    if request.method == "GET":
        rec_user = Record.objects.filter(user_id=request.user.id).all()
        return render(request, 'all_records.html', {'records': rec_user})


@login_required
def detail_record(request, record_id):
    if request.method == "GET":
        record = Record.objects.filter(id=record_id).first()
        if record.user_id != request.user.id:
            context = {'form': AuthenticationForm()}
            return render(request, 'login.html', context)
        context = {'record': record}
        return render(request, 'detail_record.html', context)


@login_required
def edit_record(request, record_id):
    if request.method == "GET":
        record = Record.objects.filter(id=record_id).first()
        if record.user_id != request.user.id:
            context = {'form': AuthenticationForm()}
            return render(request, 'login.html', context)
        record.delete_image = False
        context = {'form': RecordForm(model_to_dict(record)), 'record': record}
        return render(request, 'edit_record.html', context)
    elif request.method == "POST":
        form = RecordForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            record = Record.objects.get(id=record_id)
            record.heading = data['heading']
            record.text = data['text']
            if data['image'] is not None:
                record.image.delete()
                record.image = data['image']
            record.delete_image = data['delete_image']
            if record.delete_image:
                record.image.delete()
            record.save()
            messages.success(request, 'Record details updated.')
            return redirect('detail_record', record_id)


@login_required
def delete_record(request, record_id):
    record = Record.objects.filter(id=record_id).first()
    if record.user_id != request.user.id:
        context = {'form': AuthenticationForm()}
        return render(request, 'login.html', context)
    if request.method == 'POST':
        record = Record.objects.filter(id=record_id).first()
        record.delete()
        messages.success(request, 'Record was deleted.')
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

            subject, from_email, to = 'Sending your record from Diary', 'antonkomp1@gmail.com', user.email
            html_content = loader.render_to_string('email/send_record.html', {'user': user, 'form': record}).strip()
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.content_subtype = 'html'
            msg.mixed_subtype = 'related'
            if record.image:
                image = MIMEImage(record.image.read())
                image.add_header('Content-ID', '<{}>'.format(record.image_filename))
                msg.attach(image)
            msg.send()
            messages.success(request, 'The record was successfully sent to email!')
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
