# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-01 10:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('slides', '0002_auto_20161024_0717'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='date',
            new_name='date_planned',
        ),
        migrations.RemoveField(
            model_name='event',
            name='state',
        ),
        migrations.AddField(
            model_name='event',
            name='date_finished',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='date_started',
            field=models.DateTimeField(null=True),
        ),
    ]
