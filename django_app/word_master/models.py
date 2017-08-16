# _*_ encoding:utf-8 _*_
from __future__ import unicode_literals
from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser


class UserProfile(AbstractUser):
    nick_name = models.CharField(blank=True,
                                 verbose_name=u"昵称",
                                 max_length=100)
    avatar = models.ImageField(upload_to="images/%Y/%m",
                               verbose_name=u"头像",
                               max_length=200)
    mobile_phone = models.CharField(blank=True,
                                    null=True,
                                    verbose_name=u"手机号",
                                    max_length=20)

    class Meta:
        verbose_name = u"用户信息"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.username
