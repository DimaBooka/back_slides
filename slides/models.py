from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Presentation(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(max_length=4096)
    slides = models.FileField()
    thumbnail = models.ImageField()
    creator = models.ForeignKey(User)
    date_created = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField()

    def __str__(self):
        return self.name


class Commentary(models.Model):
    author = models.ForeignKey(User)
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
