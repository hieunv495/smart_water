# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-08 16:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20171108_2206'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='waterprice',
            name='begin_value',
        ),
        migrations.RemoveField(
            model_name='waterprice',
            name='end_value',
        ),
        migrations.AddField(
            model_name='waterprice',
            name='max_value',
            field=models.IntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='waterprice',
            name='min_value',
            field=models.IntegerField(default=-1),
        ),
    ]