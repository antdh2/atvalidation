# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-11 23:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('autotask_web_app', '0015_auto_20160811_2346'),
    ]

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254)),
            ],
        ),
        migrations.AlterField(
            model_name='validation',
            name='entity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='autotask_web_app.Entity'),
        ),
    ]
