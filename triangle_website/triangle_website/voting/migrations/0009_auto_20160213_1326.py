# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-13 20:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0008_auto_20160213_1319'),
    ]

    operations = [
        migrations.RenameField(
            model_name='voter',
            old_name='id1',
            new_name='uuid',
        ),
    ]
