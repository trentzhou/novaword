from django import template
from datetime import date, timedelta

from learn.models import LearningRecord

register = template.Library()


@register.filter(name="get_total_learn_times")
def get_total_learn_times(value):
    user_id = value
    return LearningRecord.objects.filter(user_id=user_id).count()


@register.filter(name="get_recent_learn_times")
def get_recent_learn_times(value, arg):
    user_id = value
    days = arg
    start_time = date.today() - timedelta(days=days)
    return LearningRecord.objects.filter(user_id=user_id, learn_time__gt=start_time).count()