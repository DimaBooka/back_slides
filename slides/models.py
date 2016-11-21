import os

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
import urllib
from django.core.files.base import ContentFile
from rest_framework.exceptions import ValidationError


class Presentation(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(max_length=4096)
    slides = models.FileField(upload_to='presentations', max_length=255)
    thumbnail = models.ImageField(upload_to='thumbnails')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    date_created = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField()

    def save_content(self, method):
        try:
            req = urllib.request.urlopen(self.slides.name)
        except:
            self.delete_data(method)
            raise ValidationError({'error': 'Link is not valid'})
        content_length = req.headers.get("Content-Length", '')
        if content_length and int(content_length) > 2097152:
            self.delete_data(method)
            raise ValidationError({'error': 'File is bigger than 2 MB'})
        elif not content_length:
            self.delete_data(method)
            raise ValidationError({'error': 'Raw text not detected'})
        fname = os.path.basename(self.slides.name)
        self.slides.save(name=fname, content=ContentFile(req.read().decode('utf-8')))

    def delete_data(self, method):
        if method == 'create':
            Presentation.objects.filter(pk=self.pk).delete()

    def __str__(self):
        return self.name


class Commentary(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    text = models.TextField(max_length=256)
    date_created = models.DateTimeField(auto_now_add=True)
    presentation = models.ForeignKey(Presentation)

    def __str__(self):
        return self.text


class Event(models.Model):
    name = models.CharField(max_length=40)
    presentation = models.ForeignKey(Presentation)
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    date_planned = models.DateTimeField()
    date_started = models.DateTimeField(null=True)
    date_finished = models.DateTimeField(null=True)
    secret = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.name


class User(AbstractUser):
    MALE = 1
    FEMALE = 2
    UNKNOWN = 3

    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (UNKNOWN, 'Not selected'),
    )

    birth_date = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=16, null=True, blank=True)
    gender = models.IntegerField(choices=GENDER_CHOICES, default=UNKNOWN)
    all_fields_completed = models.BooleanField(default=False)

    class Meta:
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.username
