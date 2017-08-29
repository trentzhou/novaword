# -*- coding: utf-8 -*-
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.views.generic import View
#from django.http import HttpResponse
from django.shortcuts import render, redirect

from operations.models import UserMessage
from users.forms import LoginForm, RegisterForm, ForgetForm, ModifyPasswordForm
from users.models import UserProfile, EmailVerifyRecord
from utils.email_send import send_register_email


class CustomBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username)|Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class IndexView(View):
    def get(self, request):
        """
        Get index
        :param django.http.HttpRequest request:
        :return django.http.HttpResponse:
        """
        if not request.user.is_authenticated():
            return redirect(reverse("user_login"))
        return render(request, 'index.html', {
            "page": "overview"
        })


class LoginView(View):
    def get(self, request):
        return render(request, "user_login.html", {})

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get("username", "")
            pass_word = request.POST.get("password", "")
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse("index"))
                else:
                    return render(request, "user_login.html", {"msg": u"用户未激活！"})
            else:
                return render(request, "user_login.html", {"msg": u"用户名或密码错误！"})
        else:
            return render(request, "user_login.html", {"login_form": login_form})


class LogoutView(View):
    """
    用户登出
    """
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse("index"))


class RegisterView(View):
    """
    用户注册
    """
    def get(self, request):
        register_form = RegisterForm()
        return render(request, "user_register.html", {'register_form':register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get("email", "")
            if UserProfile.objects.filter(email=user_name):
                return render(request, "user_register.html", {
                    "register_form":register_form,
                    "msg":"用户{0}已经存在".format(user_name)
                })
            pass_word = request.POST.get("password", "")
            user_profile = UserProfile()
            user_profile.nick_name = register_form.data["nickname"]
            user_profile.username = user_name
            user_profile.email = user_name
            user_profile.is_active = False
            user_profile.password = make_password(pass_word)
            user_profile.save()

            #写入欢迎注册消息
            if False:
                user_message = UserMessage()
                user_message.user = user_profile
                user_message.message = "欢迎注册"
                user_message.save()

            send_register_email(user_name, "register", request.get_host())
            return render(request, "user_login.html", {"login_title": u"注册成功，请登录"})
        else:
            return render(request, "user_register.html", {"register_form": register_form})


class AcivateUserView(View):
    def get(self, request, activate_code):
        record = EmailVerifyRecord.objects.filter(code=activate_code).get()
        if record:
            email = record.email
            user = UserProfile.objects.get(email=email)
            user.is_active = True
            user.save()

            # 删除该用户的所有的激活链接
            EmailVerifyRecord.objects.filter(email=email).delete()
        else:
            return render(request, "activate_fail.html")
        return render(request, "user_login.html")


class ForgetPasswordView(View):
    def get(self, request):
        forget_form = ForgetForm()
        return render(request, "forget_password.html", {"forget_form":forget_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get("email", "")
            # 检查用户是否存在
            if not UserProfile.objects.filter(email=email):
                return render(request, "forget_password.html", {
                    "forget_form": forget_form,
                    "msg": u"用户不存在"
                })
            send_register_email(email, "forget", request.get_host())
            return render(request, "send_success.html")
        else:
            return render(request, "forget_password.html", {"forget_form":forget_form})


class ResetPasswordView(View):
    def get(self, request, activate_code):
        record = EmailVerifyRecord.objects.filter(code=activate_code).get()
        if record:
            email = record.email
            return render(request, "password_reset.html", {"email":email})
        else:
            return render(request, "activate_fail.html")
        return render(request, "user_login.html")


class ModifyPasswordView(View):
    def post(self, request):
        modify_form = ModifyPasswordForm(request.POST)
        if modify_form.is_valid():
            password = request.POST.get("password", "")
            email = request.POST.get("email", "")
            user = UserProfile.objects.get(email=email)
            user.password = make_password(password)
            user.is_active = True
            user.save()

            # 删除该用户的所有的激活链接
            EmailVerifyRecord.objects.filter(email=email).delete()
            return render(request, "user_login.html")
        else:
            email = request.POST.get("email", "")
            return render(request, "password_reset.html", {"email":email, "reset_form":modify_form})
