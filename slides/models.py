from django.conf import settings
from django.db import models


class Presentation(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(max_length=4096)
    slides = models.FileField()
    thumbnail = models.ImageField()
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
