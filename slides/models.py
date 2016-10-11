from django.db import models


class Presentation(models.Model):
    name = models.CharField(max_length=40)
    description = models.TextField(max_length=4096)
    slides = models.FileField(upload_to='static/media/presentations')
    thumbnail = models.ImageField()
    creator = models.ForeignKey()
