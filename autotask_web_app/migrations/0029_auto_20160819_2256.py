# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-19 21:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('autotask_web_app', '0028_auto_20160819_2248'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='company_id',
        ),
        migrations.AddField(
            model_name='profile',
            name='company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='autotask_web_app.Company'),
            preserve_default=False,
        ),
    ]
