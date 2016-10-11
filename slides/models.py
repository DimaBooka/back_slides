from django.db import models


class Presentation(models.Model):
    name = models.CharField(max_length=40)
    description = models.TextField(max_length=4096)
    slides = models.FileField(upload_to='static/media/presentations')
    thumbnail = models.ImageField()
    # creator = models.ForeignKey()
    publish_date = models.DateTimeField()
    published = models.BooleanField()
    comments = models.ForeignKey(Commentary)

    def __str__(self):
        return self.name


class Commentary(models.Model):
    # author = models.ForeignKey()
    text = models.TextField(max_length=255)
    publish_date = models.DateTimeField()

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
