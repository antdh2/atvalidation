# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-19 22:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autotask_web_app', '0029_auto_20160819_2256'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='password',
            field=models.CharField(default='test', max_length=254),
            preserve_default=False,
        ),
    ]