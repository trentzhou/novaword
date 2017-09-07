# -*- coding: utf-8 -*-
import xadmin
from .models import Word, WordBook, WordUnit, WordInUnit, LearningPlan, LearningRecord


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
    search_fields = list_display
    list_filter = list_display
    model_icon = 'fa fa-book'


class WordUnitAdmin(object):
    list_display = ['description', 'book', 'order']
    search_fields = list_display
    list_filter = list_display
    model_icon = 'fa fa-calendar'


class WordInUnitAdmin(object):
    list_display = ['word', 'unit', 'order', 'simple_meaning']
    search_fields = list_display
    list_filter = list_display
    model_icon = 'fa fa-chain'


class LearningPlanAdmin(object):
    list_display = ['user', 'unit']
    search_fields = list_display
    list_filter = list_display
    model_icon = 'fa fa-check'


class LearningRecordAdmin(object):
    list_display = ['user', 'unit', 'type', 'learn_time', 'correct_rate']
    search_fields = ['user', 'unit', 'type']
    list_filter = list_display
    model_icon = 'fa fa-tasks'


xadmin.site.register(Word, WordAdmin)
xadmin.site.register(WordBook, WordBookAdmin)
xadmin.site.register(WordUnit, WordUnitAdmin)
xadmin.site.register(WordInUnit, WordInUnitAdmin)
xadmin.site.register(LearningPlan, LearningPlanAdmin)
xadmin.site.register(LearningRecord, LearningRecordAdmin)
