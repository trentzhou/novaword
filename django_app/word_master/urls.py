"""word_master URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
import xadmin

from users.views import IndexView, LoginView, LogoutView, \
    RegisterView, AcivateUserView, ForgetPasswordView, ResetPasswordView, ModifyPasswordView

urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^$', IndexView.as_view(), name="index"),
    url(r'^login/$', LoginView.as_view(), name="user_login"),
    url(r'^logout/$', LogoutView.as_view(), name="user_logout"),
    url(r'^register/$', RegisterView.as_view(), name="user_register"),
    url(r'^forget_password/$', ForgetPasswordView.as_view(), name="forget_password"),
    url(r'^reset_password/(?P<activate_code>.*)/$', ResetPasswordView.as_view(), name="reset_password"),
    url(r'^modify_password/$', ModifyPasswordView.as_view(), name="modify_password"),
    url(r'^activate/(?P<activate_code>.*)/$', AcivateUserView.as_view(), name="user_active"),
    #url(r'^reset_password/$', ResetPasswordView.as_view, name="reset_password"),
    url(r'^captcha/', include('captcha.urls'))
]
