# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-14 15:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='brother',
            name='user',
        ),
        migrations.DeleteModel(
            name='Brother',
        ),
    ]
