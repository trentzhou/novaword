# _*_ encoding:utf-8 _*_
from __future__ import unicode_literals
from datetime import datetime
from django.db import models
from learn.models import WordBook, Word
from users.models import UserProfile, UserGroup


class Quiz(models.Model):
    description = models.CharField(blank=False,
                                   max_length=200, verbose_name=u"描述")
    book = models.ForeignKey(WordBook, verbose_name=u"单词书")
    group = models.ForeignKey(UserGroup, verbose_name=u"群组")
    max_total_time = models.IntegerField(default=7200,
                                         verbose_name=u"最大总答题时间（秒）")
    max_word_time = models.IntegerField(default=120,
                                        verbose_name=u"单词最大答题时间（秒）")
    password = models.CharField(blank=True, max_length=100,
                                verbose_name=u"参加测试的密码")
    expire_date = models.DateField(blank=True, verbose_name=u"过期日期")

    class Meta:
        verbose_name = u"测试"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.description


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, verbose_name=u"测试")
    word = models.ForeignKey(Word, verbose_name=u"单词")
    quiz_format = models.IntegerField(choices=((1, u"看英文选中文"),
                                               (2, u"看中文选英文"),
                                               (3, u"拼写")),
                                      verbose_name=u"测试形式")

    class Meta:
        verbose_name = u"测试题"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return "{0}".format(self.word)


class QuizResult(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name=u"用户")
    quiz = models.ForeignKey(Quiz, verbose_name=u"测试")
    start_time = models.DateTimeField(default=datetime.now,
                                      verbose_name=u"开始时间")
    finish_time = models.DateTimeField(null=True, verbose_name=u"完成时间")

    class Meta:
        verbose_name = u"测试结果"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return "{0} - {1}".format(self.user.username, self.quiz.description)


class QuizQuestionResult(models.Model):
    quiz_result = models.ForeignKey(QuizResult, verbose_name=u"测试结果")
    quiz_question = models.ForeignKey(QuizQuestion, verbose_name=u"问题")
    is_correct = models.BooleanField(default=False, verbose_name=u"答对了")

    class Meta:
        verbose_name = u"题目解答"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return "{0} - {1}".format(self.quiz_question, self.quiz_result)
