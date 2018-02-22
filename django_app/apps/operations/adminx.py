# -*- coding: utf-8 -*-
import xadmin
from .models import UserMessage, GroupBook, GroupLearningPlan, UserFeedback


class UserMessageAdmin(object):
    list_display = ['title', 'message', 'to_user', 'from_user', 'has_read', 'add_time']
    search_fields = ['title', 'message', 'from_user__username']
    list_filter = ['title', 'message', 'to_user', 'from_user__username', 'has_read', 'add_time']
    model_icon = 'fa fa-comments'


class GroupBookAdmin(object):
    list_display = ['group', 'book']
    search_fields = ['group__description', 'book__description']
    list_filter = list_display
    model_icon = 'fa fa-check'


class GroupLearningPlanAdmin(object):
    list_display = ['group', 'unit']
    search_fields = ['group__description', 'unit__description']
    list_filter = list_display
    model_icon = 'fa fa-check'


class UserFeedbackAdmin(object):
    list_display = ['reporter', 'title', 'detail']
    search_fields = ['title', 'detail']
    list_filter = list_display
    model_icon = 'fa fa-question'


xadmin.site.register(UserMessage, UserMessageAdmin)
xadmin.site.register(GroupBook, GroupBookAdmin)
xadmin.site.register(GroupLearningPlan, GroupLearningPlanAdmin)
xadmin.site.register(UserFeedback, UserFeedbackAdmin)