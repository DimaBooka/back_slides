from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class Presentation(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(max_length=4096)
    slides = models.FileField(upload_to='presentations')
    thumbnail = models.ImageField(upload_to='thumbnails')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    date_created = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField()

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
    date = models.DateTimeField()
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

    class Meta:
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.username
