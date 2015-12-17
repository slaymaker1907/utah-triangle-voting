# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-16 22:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0002_auto_20151216_1234'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnonVoter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('election', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='voting.Election')),
            ],
        ),
        migrations.AddField(
            model_name='vote',
            name='voter',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='voting.AnonVoter'),
            preserve_default=False,
        ),
    ]
