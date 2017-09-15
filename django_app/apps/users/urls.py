# -*- coding: utf-8 -*-
from django.conf.urls import url

from users.forms import AjaxChangeNickNameForm
from users.views import UserInfoView, AvatarUploadView, AjaxChangeNickNameView, \
    AjaxGetEmailVerificationView, AjaxUpdateEmailView, AjaxChangePasswordView, AjaxChangeMobileView, MyGroupView, \
    GroupListView, GroupDetailView, AjaxJoinGroupView, AjaxLeaveGroupView, UserContactView, AjaxApproveJoinGroupView, \
    AjaxApproveLeaveGroupView, AjaxRejectRequestView, AjaxCreateGroupView, AjaxApproveCreateGroupView

urlpatterns = [
    url(r'^profile/$', UserInfoView.as_view(), name="users.profile"),
    url(r'^contact/(?P<user_id>\d+)$', UserContactView.as_view(), name="users.contact"),
    # 编辑用户
    url(r'^avatar/upload/$', AvatarUploadView.as_view(), name="user.avatar_upload"),
    url(r'^ajax-change-nick-name/$', AjaxChangeNickNameView.as_view(), name="user.ajax_change_nick_name"),
    url(r'^ajax-get-email-verification/$', AjaxGetEmailVerificationView.as_view(), name="user.ajax_get_email_verification"),
    url(r'^ajax-update-email/$', AjaxUpdateEmailView.as_view(), name="user.ajax_update_email"),
    url(r'^ajax-change-password/$', AjaxChangePasswordView.as_view(), name="user.ajax_change_password"),
    url(r'^ajax-change-mobile/$', AjaxChangeMobileView.as_view(), name="user.ajax_change_mobile"),
    # 用户组
    url(r'^my-gorups/$', MyGroupView.as_view(), name="user.my_groups"),
    url(r'^groups/$', GroupListView.as_view(), name="user.groups"),
    url(r'^gorups/(?P<group_id>\d+)/$', GroupDetailView.as_view(), name="user.group_detail"),
    url(r'^ajax-join-group/$', AjaxJoinGroupView.as_view(), name="user.join_group"),
    url(r'^ajax-leave-group/$', AjaxLeaveGroupView.as_view(), name="user.leave_group"),
    url(r'^ajax-create-group/$', AjaxCreateGroupView.as_view(), name="user.create_group"),
    url(r'^ajax-approve-join-group/$', AjaxApproveJoinGroupView.as_view(), name="user.approve_join_group"),
    url(r'^ajax-approve-leave-group/$', AjaxApproveLeaveGroupView.as_view(), name="user.approve_leave_group"),
    url(r'^ajax-approve-create-group/$', AjaxApproveCreateGroupView.as_view(), name="user.approve_create_group"),
    url(r'^ajax-reject-request/$', AjaxRejectRequestView.as_view(), name="user.reject_request"),
]