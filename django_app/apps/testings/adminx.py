# -*- coding: utf-8 -*-
import xadmin
from .models import Quiz, QuizQuestion, QuizResult


class QuizAdmin(object):
    list_display = ['description',
                    'author',
                    'book',
                    'groups',
                    'max_total_time',
                    'max_word_time',
                    'password',
                    'is_public']
    search_fields = ['description', 'author__nick_name', 'book__description']
    list_filter = ['description',
                   'author',
                   'groups',
                   'book__description',
                   'max_total_time',
                   'max_word_time',
                   'password',
                   'is_public']
    model_icon = 'fa fa-table'


class QuizQuestionAdmin(object):
    list_display = ['word', 'quiz', 'quiz_format']
    search_fields = ['word__word__spelling', 'quiz__description', 'word__unit__description']
    list_filter = ['word__word__spelling', 'quiz__description', 'quiz_format']
    model_icon = 'fa fa-question'


class QuizResultAdmin(object):
    list_display = ['user', 'quiz', 'start_time', 'finish_time', 'correct_count']
    search_fields = ['user__nick_name', 'quiz__description']
    list_filter = ['user__username',
                   'quiz__description',
                   'start_time',
                   'finish_time',
                   'correct_count']
    model_icon = 'fa fa-bars'


xadmin.site.register(Quiz, QuizAdmin)
xadmin.site.register(QuizQuestion, QuizQuestionAdmin)
xadmin.site.register(QuizResult, QuizResultAdmin)
