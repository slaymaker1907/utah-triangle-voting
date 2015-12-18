# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-17 15:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0003_auto_20151216_1527'),
    ]

    operations = [
        migrations.CreateModel(
            name='Passcode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=255)),
                ('election', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='voting.Election', unique=True)),
            ],
        ),
    ]
