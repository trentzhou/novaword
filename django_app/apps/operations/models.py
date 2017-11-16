# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django.db import models

from learn.models import WordBook, WordUnit
from users.models import UserProfile, Group


# Create your models here.


class UserMessage(models.Model):
    # const values
    MSG_TYPE_USER = 0
    MSG_TYPE_CREATE_ORGANIZATION    = 1
    MSG_TYPE_CREATE_ORGANIZATION_OK = 2
    MSG_TYPE_CREATE_GROUP           = 3
    MSG_TYPE_CREATE_GROUP_OK        = 4
    MSG_TYPE_DELETE_GROUP           = 5
    MSG_TYPE_DELETE_GROUP_OK        = 6
    MSG_TYPE_JOIN_GROUP             = 7
    MSG_TYPE_JOIN_GROUP_OK          = 8
    MSG_TYPE_LEAVE_GROUP            = 9
    MSG_TYPE_LEAVE_GROUP_OK         = 10
    MSG_TYPE_APPROVED               = 100
    MSG_TYPE_REJECTED               = 110

    to_user = models.IntegerField(default=0, verbose_name=u"收消息的用户")
    from_user = models.ForeignKey(UserProfile, default=None, verbose_name=u"发送消息的用户", null=True)
    title = models.CharField(max_length=100, verbose_name=u"消息标题", default="", blank=True)
    message = models.CharField(max_length=500, verbose_name=u"消息内容")
    message_type = models.IntegerField(verbose_name=u"消息类型",
                                       choices=(
                                           (0, u"用户消息"),
                                           (1, u"申请创建学校"),
                                           (2, u"成功创建学校"),
                                           (3, u"申请创建班级"),
                                           (4, u"成功创建班级"),
                                           (5, u"申请删除班级"),
                                           (6, u"成功删除班级"),
                                           (7, u"申请加入班级"),
                                           (8, u"成功加入班级"),
                                           (9, u"申请退出班级"),
                                           (10, u"成功退出班级"),
                                           (100, u"请求被批准"),
                                           (110, u"请求被拒绝"),
                                       ),
                                       default=0)
    has_read = models.BooleanField(default=False, verbose_name=u"已读")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")
    model_icon = 'fa fa-envelope-open'

    class Meta:
        verbose_name = u"用户消息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u"{0} - {1}".format(self.from_user, self.message)


class GroupBook(models.Model):
    group = models.ForeignKey(Group, verbose_name=u"班级")
    book = models.ForeignKey(WordBook, verbose_name=u"单词书")

    class Meta:
        verbose_name = u"班级课本"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u"{0} - {1}".format(self.group.description, self.unit)


class GroupLearningPlan(models.Model):
    group = models.ForeignKey(Group, verbose_name=u"班级")
    unit = models.ForeignKey(WordUnit, verbose_name=u"单元")

    class Meta:
        verbose_name = u"班级学习计划"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u"{0} - {1}".format(self.group.description, self.unit)

