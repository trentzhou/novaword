import datetime
import os

from django.conf import settings

from pytz import timezone


def get_now():
    """
    Get current time with zone information
    :return:
    """
    local_tz = timezone(os.getenv('TZ', settings.TIME_ZONE))
    return datetime.datetime.now(tz=local_tz)
