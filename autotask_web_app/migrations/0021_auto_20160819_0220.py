# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-19 01:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autotask_web_app', '0020_entity_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entity',
            name='name',
            field=models.CharField(max_length=254, unique=True),
        ),
    ]