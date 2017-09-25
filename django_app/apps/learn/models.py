# _*_ encoding:utf-8 _*_
from __future__ import unicode_literals

from datetime import datetime
from django.db import models
from django.db.models import Q

from users.models import UserProfile


class Word(models.Model):
    spelling = models.CharField(blank=False, max_length=100,
                                verbose_name=u"拼写")
    pronounciation_us = models.CharField(blank=True, max_length=100,
                                         verbose_name=u"美式发音")
    pronounciation_uk = models.CharField(blank=True, max_length=100,
                                         verbose_name=u"英式发音")
    mp3_us_url = models.URLField(blank=True,
                                 verbose_name=u"美式发音mp3")
    mp3_uk_url = models.URLField(blank=True,
                                 verbose_name=u"英式发音mp3")
    short_meaning = models.CharField(blank=False, max_length=300,
                                     verbose_name=u"简单解释")
    detailed_meanings = models.TextField(blank=True, verbose_name=u"详细解释")
    wrong_meaning1 = models.CharField(blank=True, max_length=100,
                                      verbose_name=u"错误解释1")
    wrong_meaning2 = models.CharField(blank=True, max_length=100,
                                      verbose_name=u"错误解释2")
    wrong_meaning3 = models.CharField(blank=True, max_length=100,
                                      verbose_name=u"错误解释3")

    class Meta:
        verbose_name = u"单词"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.spelling


class WordBook(models.Model):
    description = models.CharField(blank=True, max_length=200,
                                   verbose_name=u"描述")
    uploaded_by = models.ForeignKey(UserProfile, verbose_name=u"上传人")
    max_word_learn_time = models.IntegerField(default=1000,
                                              verbose_name=u"每个单词最长学习秒数")
    max_unit_learn_time = models.IntegerField(default=6000,
                                              verbose_name=u"每个单元最长学习秒数")
    max_working_units = models.IntegerField(default=3,
                                            verbose_name=u"最多几个单元同时在学习")

    class Meta:
        verbose_name = u"单词书"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.description


class WordUnit(models.Model):
    book = models.ForeignKey(WordBook, verbose_name=u"单词书")
    description = models.CharField(blank=True, max_length=100,
                                   verbose_name=u"描述")
    order = models.IntegerField(default=1, verbose_name=u"顺序")

    class Meta:
        verbose_name = u"单元"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u"{0} - {1}".format(self.book.description, self.description)

    def is_planned(self, user):
        if LearningPlan.objects.filter(unit=self, user=user).count():
            return True
        return False

    def learn_count(self, user):
        return self.learningrecord_set.filter(Q(type=1)|Q(type=2), user=user).count()

    def review_count(self, user):
        return self.learningrecord_set.filter(user=user, type=3).count()


class WordInUnit(models.Model):
    word = models.ForeignKey(Word, verbose_name=u"单词")
    unit = models.ForeignKey(WordUnit, verbose_name=u"单元")
    order = models.IntegerField(default=1, verbose_name=u"顺序")
    simple_meaning = models.CharField(default="", verbose_name=u"简单解释", max_length=100)

    class Meta:
        verbose_name = u"单元单词"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u"{0} - {1}".format(self.word, self.unit)


class LearningPlan(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name=u"用户")
    unit = models.ForeignKey(WordUnit, verbose_name=u"单元")

    class Meta:
        verbose_name = u"学习计划"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u"{0} - {1}".format(self.user.username, self.unit)


class LearningRecord(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name=u"用户")
    unit = models.ForeignKey(WordUnit, verbose_name=u"单元")
    type = models.IntegerField(choices=((1, u"初次学习"),
                                        (2, u"单元测试"),
                                        (3, u"复习")),
                               default=2,
                               verbose_name=u"学习类型")
    learn_time = models.DateTimeField(default=datetime.now,
                                      verbose_name=u"学习时间")
    correct_rate = models.IntegerField(default=100, verbose_name=u"正确率")

    class Meta:
        verbose_name = u"学习记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return u"{0} - {1}".format(self.user.username, self.unit)
