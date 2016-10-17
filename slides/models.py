from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db import models
from django.contrib.sites.models import Site

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
    PLANNED = 1
    DONE = 2
    CANCELED = 3
    POSTPONED = 4

    STATE_CHOICES = (
        (PLANNED, "Planned"),
        (DONE, "Done"),
        (CANCELED, "Canceled"),
        (POSTPONED, "Postponed"),
    )

    name = models.CharField(max_length=40)
    presentation = models.ForeignKey(Presentation)
    date = models.DateTimeField()
    state = models.IntegerField(choices=STATE_CHOICES, default=PLANNED)

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
