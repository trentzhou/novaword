# -*- coding: utf-8 -*-
import xadmin
from xadmin.plugins.auth import UserAdmin
from .models import EmailVerifyRecord, Group, UserGroup, Organization, UserProfile


class BaseSetting(object):
    enable_themes = True
    use_bootswatch = True


class GlobalSetting(object):
    site_title = u"Nova背单词"
    site_footer = u"Nova背单词"
    #menu_style = "accordion"


class UserProfileAdmin(UserAdmin):
    list_display = ('username', 'nick_name', 'email', 'mobile_phone')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'nick_name', 'email', 'mobile_phone')


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
    list_display = ['user', 'group', 'role', 'student_id', 'join_time']
    search_fields = ['user__nick_name', 'group__name', 'role', 'student_id']
    list_filter = ['user', 'group', 'role', 'student_id', 'join_time']
    model_icon = 'fa fa-link'


xadmin.site.unregister(UserProfile)
xadmin.site.register(UserProfile, UserProfileAdmin)
xadmin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
xadmin.site.register(Organization, OrganizationAdmin)
xadmin.site.register(Group, GroupAdmin)
xadmin.site.register(UserGroup, UserGroupAdmin)
xadmin.site.register(xadmin.views.BaseAdminView, BaseSetting)
xadmin.site.register(xadmin.views.CommAdminView, GlobalSetting)
