# -*- coding: utf-8 -*-
import xadmin
from .models import UserMessage


class UserMessageAdmin(object):
    list_display = ['title', 'message', 'to_user', 'from_user', 'has_read', 'add_time']
    search_fields = ['title', 'message', 'from_user__username']
    list_filter = ['title', 'message', 'to_user', 'from_user__username', 'has_read', 'add_time']
    model_icon = 'fa fa-comments'


xadmin.site.register(UserMessage, UserMessageAdmin)
