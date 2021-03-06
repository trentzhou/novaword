# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-02-22 14:12
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('operations', '0008_groupbook_grouplearningplan'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='标题')),
                ('detail', models.TextField(verbose_name='消息描述')),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='汇报人')),
            ],
            options={
                'verbose_name': '用户反馈',
                'verbose_name_plural': '用户反馈',
            },
        ),
    ]
