from django import template
from datetime import date, timedelta

from users.models import UserGroup

register = template.Library()


@register.filter(name="is_teacher")
def is_teacher(value):
    user_id = value
    if UserGroup.objects.filter(user_id=user_id, role__gt=1).count():
        return True
    return False

