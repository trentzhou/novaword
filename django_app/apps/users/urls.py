from django.conf.urls import url

from users.forms import AjaxChangeNickNameForm
from users.views import UserInfoView, ClassListView, AvatarUploadView, AjaxChangeNickNameView, \
    AjaxGetEmailVerificationView, AjaxUpdateEmailView, AjaxChangePasswordView, AjaxChangeMobileView

urlpatterns = [
    url(r'^profile/$', UserInfoView.as_view(), name="users.profile"),
    url(r'^classes/$', ClassListView.as_view(), name="users.classes"),
    url(r'^avatar/upload/$', AvatarUploadView.as_view(), name="user.avatar_upload"),
    url(r'^ajax-change-nick-name/$', AjaxChangeNickNameView.as_view(), name="user.ajax_change_nick_name"),
    url(r'^ajax-get-email-verification/$', AjaxGetEmailVerificationView.as_view(), name="user.ajax_get_email_verification"),
    url(r'^ajax-update-email/$', AjaxUpdateEmailView.as_view(), name="user.ajax_update_email"),
    url(r'^ajax-change-password/$', AjaxChangePasswordView.as_view(), name="user.ajax_change_password"),
    url(r'^ajax-change-mobile/$', AjaxChangeMobileView.as_view(), name="user.ajax_change_mobile"),
]