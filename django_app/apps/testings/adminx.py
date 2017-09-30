# -*- coding: utf-8 -*-
import xadmin
from .models import Quiz, QuizQuestion, QuizResult, QuizQuestionResult


class QuizAdmin(object):
    list_display = ['description',
                    'author',
                    'book',
                    'groups',
                    'max_total_time',
                    'max_word_time',
                    'password']
    search_fields = list_display
    list_filter = ['description',
                   'author',
                   'groups',
                   'book__description',
                   'max_total_time',
                   'max_word_time',
                   'password']
    model_icon = 'fa fa-table'


class QuizQuestionAdmin(object):
    list_display = ['word', 'quiz', 'quiz_format']
    search_fields = list_display
    list_filter = ['word__word__spelling', 'quiz__description', 'quiz_format']
    model_icon = 'fa fa-question'


class QuizResultAdmin(object):
    list_display = ['user', 'quiz', 'state', 'start_time', 'finish_time']
    search_fields = ['user', 'quiz']
    list_filter = ['user__username',
                   'quiz__description',
                   'state',
                   'start_time',
                   'finish_time']
    model_icon = 'fa fa-bars'


class QuizQuestionResultAdmin(object):
    list_display = ['quiz_question', 'quiz_result', 'is_correct']
    search_fields = list_display
    list_filter = ['quiz_question__word__spelling',
                   'quiz_result__quiz__description', 'is_correct']
    model_icon = 'fa fa-pencil'


xadmin.site.register(Quiz, QuizAdmin)
xadmin.site.register(QuizQuestion, QuizQuestionAdmin)
xadmin.site.register(QuizResult, QuizResultAdmin)
xadmin.site.register(QuizQuestionResult, QuizQuestionResultAdmin)
