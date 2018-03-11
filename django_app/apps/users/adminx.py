# -*- coding: utf-8 -*-
import xadmin
from .models import EmailVerifyRecord, Group, UserGroup, Organization


class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True


class GlobalSetting(object):
    site_title = u"Nova背单词"
    site_footer = u"Nova背单词"
    #menu_style = "accordion"


class EmailVerifyRecordAdmin(object):
    list_display = ['code', 'email', 'send_type', 'send_time']
    search_fields = ['code', 'email', 'send_type']
    list_filter = ['code', 'email', 'send_type', 'send_time']
    model_icon = 'fa fa-envelope'


class OrganizationAdmin(object):
    list_display = ['name', 'description', 'create_time']
    search_fields = ['name', 'description']
    list_filter = ['name', 'description', 'create_time']
    model_icon = 'fa fa-institution'


class GroupAdmin(object):
    list_display = ['name', 'description', 'organization', 'is_admin', 'create_time', 'banner']
    search_fields = ['name', 'description', 'organization__description', 'banner']
    list_filter = ['name', 'description', 'organization', 'is_admin', 'create_time']
    model_icon = 'fa fa-list'


class UserGroupAdmin(object):
    list_display = ['user', 'group', 'role', 'join_time']
    search_fields = ['user', 'group', 'role']
    list_filter = ['user', 'group', 'role', 'join_time']
    model_icon = 'fa fa-link'


xadmin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
xadmin.site.register(Organization, OrganizationAdmin)
xadmin.site.register(Group, GroupAdmin)
xadmin.site.register(UserGroup, UserGroupAdmin)
xadmin.site.register(xadmin.views.BaseAdminView, BaseSetting)
xadmin.site.register(xadmin.views.CommAdminView, GlobalSetting)
