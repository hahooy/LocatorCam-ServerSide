# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-06-19 04:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locator_cam_app', '0019_auto_20160619_0140'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='channel',
            name='channel_managers',
        ),
        migrations.AddField(
            model_name='channel',
            name='administrators',
            field=models.ManyToManyField(related_name='admin_channels', to='locator_cam_app.UserProfile'),
        ),
    ]
