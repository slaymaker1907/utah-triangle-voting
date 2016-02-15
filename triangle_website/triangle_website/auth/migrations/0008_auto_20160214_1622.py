# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-14 23:22
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('triangle_website.auth', '0007_auto_20160214_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brother',
            name='initiation_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='brother',
            name='phone',
            field=models.CharField(default='', max_length=30, validators=[django.core.validators.RegexValidator(message='Invalid phone number. (xxx)-xxx-xxxx is valid.', regex='^\\+?1?\\(?\\d{3,3}\\)? *-? *\\d{3,3} *-? *\\d{4,4}$')]),
        ),
    ]
