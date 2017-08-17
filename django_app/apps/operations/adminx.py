# -*- coding: utf-8 -*-
import xadmin
from .models import UserMessage


class UserMessageAdmin(object):
    list_display = ['message', 'user', 'has_read', 'add_time']
    search_fields = ['message', 'user__username']
    list_filter = ['message', 'user__username', 'has_read', 'add_time']
    model_icon = 'fa fa-comments'


xadmin.site.register(UserMessage, UserMessageAdmin)
