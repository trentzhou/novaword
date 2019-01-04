from django import template
from datetime import date, timedelta

from learn.models import LearningRecord, WordBook

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


@register.filter(name="get_latest_unit")
def get_latest_unit(value):
    user_id = value
    try:
        record = LearningRecord.objects.filter(user_id=user_id).order_by("-learn_time").first()
        return str(record.unit)
    except:
        return ""


@register.filter(name="readable_time")
def readable_time(seconds):
    """
    将秒数转换成人比较容易读的时间值
    :param seconds: 秒数
    :return:
    """
    minutes = int(seconds / 60)
    s = int(seconds) % 60
    return "{0}分{1}秒".format(minutes, s)


@register.filter(name="is_book_maintainer")
def is_book_maintainer(user_id, book_id):
    try:
        book = WordBook.objects.get(id=book_id)
        if book.uploaded_by.id == user_id:
            return True
        if book.maintainers.filter(id=user_id).count() > 0:
            return True
    except:
        pass
    return False


@register.assignment_tag
def define(val=None):
    return val
