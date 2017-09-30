# -*- coding: utf-8 -*-
from django import forms

from testings.models import Quiz


class CreateQuizForm(forms.Form):
    description = forms.CharField(required=True)
    max_total_time = forms.IntegerField()
    max_word_time = forms.IntegerField()
    book_id = forms.IntegerField(required=True)

