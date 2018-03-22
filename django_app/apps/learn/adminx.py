# -*- coding: utf-8 -*-
import xadmin
from .models import Word, WordBook, WordUnit, WordInUnit, LearningPlan, LearningRecord, ErrorWord, UserTask


class WordAdmin(object):
    list_display = ['spelling',
                    'pronounciation_us',
                    'pronounciation_uk',
                    'short_meaning',
                    'detailed_meanings',
                    'wrong_meaning1',
                    'wrong_meaning2',
                    'wrong_meaning3']
    search_fields = list_display
    list_filter = list_display
    model_icon = 'fa fa-bars'
    relfield_style = 'fk-ajax'


class WordBookAdmin(object):
    list_display = ['description',
                    'uploaded_by',
                    'max_word_learn_time',
                    'max_unit_learn_time',
                    'max_working_units']
    search_fields = ['description', 'uploaded_by__username', 'uploaded_by__nick_name']
    list_filter = list_display
    model_icon = 'fa fa-book'


class WordUnitAdmin(object):
    list_display = ['description', 'book', 'order']
    search_fields = ['description', 'book__description']
    list_filter = list_display
    model_icon = 'fa fa-calendar'


class WordInUnitAdmin(object):
    list_display = ['word', 'unit', 'order', 'simple_meaning']
    search_fields = ['word__spelling', 'simple_meaning']
    list_filter = list_display
    model_icon = 'fa fa-chain'


class LearningPlanAdmin(object):
    list_display = ['user', 'unit']
    search_fields = ['user__username', 'user__nick_name', 'unit__description']
    list_filter = list_display
    model_icon = 'fa fa-check'

class LearningRecordAdmin(object):
    list_display = ['user', 'unit', 'type', 'learn_time', 'correct_rate']
    search_fields = ['user__username', 'user__nick_name', 'unit__description', 'type']
    list_filter = list_display
    model_icon = 'fa fa-tasks'


class ErrorWordAdmin(object):
    list_display = ['user', 'word', 'error_count', 'amend_count', 'latest_error_time']
    search_fields = ['user__username', 'user__nick_name', 'word__word__spelling']
    list_filter = list_display
    model_icon = 'fa fa-bug'


class UserTaskAdmin(object):
    list_display = ['user', 'unit', 'type']
    search_fields = ['user__username', 'user__nick_name', 'unit__description', 'type']
    list_filter = list_display
    model_icon = 'fa fa-tasks'


xadmin.site.register(Word, WordAdmin)
xadmin.site.register(WordBook, WordBookAdmin)
xadmin.site.register(WordUnit, WordUnitAdmin)
xadmin.site.register(WordInUnit, WordInUnitAdmin)
xadmin.site.register(LearningPlan, LearningPlanAdmin)
xadmin.site.register(LearningRecord, LearningRecordAdmin)
xadmin.site.register(ErrorWord, ErrorWordAdmin)
xadmin.site.register(UserTask, UserTaskAdmin)
