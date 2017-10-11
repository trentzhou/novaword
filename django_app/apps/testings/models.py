# _*_ encoding:utf-8 _*_
from __future__ import unicode_literals
from datetime import datetime
from django.db import models
from learn.models import WordBook, Word, WordInUnit
from users.models import UserProfile, Group


class Quiz(models.Model):
    description = models.CharField(blank=False,
                                   max_length=200, verbose_name=u"描述")
    author = models.ForeignKey(UserProfile, null=True, verbose_name=u"作者")
    book = models.ForeignKey(WordBook, verbose_name=u"单词书")
    max_total_time = models.IntegerField(default=7200,
                                         verbose_name=u"最大总答题时间（秒）")
    max_word_time = models.IntegerField(default=120,
                                        verbose_name=u"单词最大答题时间（秒）")
    password = models.CharField(blank=True, max_length=100,
                                verbose_name=u"参加测试的密码")
    groups = models.ManyToManyField(Group, verbose_name=u"班级")

    class Meta:
        verbose_name = u"考卷"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.description


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, verbose_name=u"测试")
    word = models.ForeignKey(WordInUnit, verbose_name=u"单词")
    quiz_format = models.IntegerField(choices=((0, u"随机"),
                                               (1, u"看英文选中文"),
                                               (2, u"看中文选英文"),
                                               (3, u"拼写")),
                                      default=0,
                                      verbose_name=u"测试形式")

    class Meta:
        verbose_name = u"测试题"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return "{0}".format(self.word)


class QuizResult(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name=u"用户")
    quiz = models.ForeignKey(Quiz, verbose_name=u"测试")
    start_time = models.DateTimeField(default=datetime.now,
                                      verbose_name=u"开始时间")
    finish_time = models.DateTimeField(null=True, verbose_name=u"完成时间")
    correct_count = models.IntegerField(default=0, verbose_name=u"答对题数")

    class Meta:
        verbose_name = u"答卷"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return "{0} - {1}".format(self.user.username, self.quiz.description)

