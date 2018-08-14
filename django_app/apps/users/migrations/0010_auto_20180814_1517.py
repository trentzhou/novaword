# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-08-14 15:17
from __future__ import unicode_literals

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20180813_1946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='password',
            field=models.CharField(default=users.models.generate_token, max_length=100, verbose_name='进组密码'),
        ),
    ]