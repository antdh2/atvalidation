# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-19 23:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autotask_web_app', '0032_auto_20160819_2344'),
    ]

    operations = [
        migrations.AddField(
            model_name='validation',
            name='mandatory',
            field=models.BooleanField(default=True),
        ),
    ]
