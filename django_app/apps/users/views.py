# -*- coding: utf-8 -*-
import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import View
#from django.http import HttpResponse
from django.shortcuts import render, redirect

from operations.models import UserMessage
from users.forms import LoginForm, RegisterForm, ForgetForm, ModifyPasswordForm, RegisterMobileForm, VerifySmsForm
from users.models import UserProfile, EmailVerifyRecord
from utils.email_send import send_register_email, save_email_verify_record
from utils.wilddog_sms import is_valid_phone_number, SmsClient
from word_master.settings import WILDDOG_API_KEY, WILDDOG_APP_ID


class CustomBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username)|Q(email=username)|Q(mobile_phone=username))
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
        return render(request, "user_register.html", {
            'register_form':register_form,
            'method': 'email'
        })

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get("email", "")
            if UserProfile.objects.filter(email=user_name):
                return render(request, "user_register.html", {
                    "register_form":register_form,
                    "msg":"用户{0}已经存在".format(user_name),
                    "method": "email"
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
            user_message = UserMessage()
            user_message.to_user = user_profile.id
            user_message.from_user = user_profile
            user_message.message = "欢迎注册"
            user_message.save()

            send_register_email(user_name, "register", request.get_host())
            return render(request, "user_login.html", {"login_title": u"注册成功，请登录"})
        else:
            return render(request, "user_register.html", {"register_form": register_form})


class RegisterMobileView(View):
    def get(self, request):
        register_mobile_form = RegisterMobileForm()
        return render(request, "user_register.html", {
            "register_mobile_form": register_mobile_form,
            "method": "mobile"
        })

    def post(self, request):
        register_mobile_form = RegisterMobileForm(request.POST)
        if register_mobile_form.is_valid():
            mobile = request.POST.get("mobile")
            password = request.POST.get("password")
            nickname = request.POST.get("nickname")

            if UserProfile.objects.filter(mobile_phone=mobile):
                return render(request, "user_register.html", {
                    "register_mobile_form": register_mobile_form,
                    "msg":"用户{0}已经存在".format(mobile),
                    "method": "mobile"
                })

            user = UserProfile()
            user.nick_name = nickname
            user.mobile_phone = mobile
            user.username = mobile
            user.is_active = True
            user.email = ""
            user.password = make_password(password)
            user.save()

            # 写入欢迎消息
            user_message = UserMessage()
            user_message.to_user = user.id
            user_message.from_user = user
            user_message.message = "欢迎注册"
            user_message.save()

            return render(request, "user_login.html", {"login_title": u"注册成功，请登录"})
        else:
            return render(request, "user_register.html", {
                "register_mobile_form": register_mobile_form,
                "method": "mobile"
            })


class UserVirificationSmsView(View):
    def post(self, request):
        mobile = request.POST.get("mobile", "")
        if is_valid_phone_number(mobile):
            c = SmsClient(WILDDOG_APP_ID, WILDDOG_API_KEY)
            result = c.send_code(str(mobile), "100000", None)
            return HttpResponse(result)
        else:
            return HttpResponse(json.dumps({
                "status": "failed"
            }), status=200)


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
            user_query = UserProfile.objects.filter(Q(email=email)|Q(mobile_phone=email))
            if not user_query:
                return render(request, "forget_password.html", {
                    "forget_form": forget_form,
                    "msg": u"用户不存在"
                })
            user = user_query.get()
            if user.email == email:
                send_register_email(email, "forget", request.get_host())
                return render(request, "send_success.html")
            elif user.mobile_phone == email:
                # 发送短消息来重置密码
                c = SmsClient(WILDDOG_APP_ID, WILDDOG_API_KEY)
                c.send_code(str(email), "100000", None)
                return render(request, "verify_sms.html", {"mobile": email})
        else:
            return render(request, "forget_password.html", {"forget_form":forget_form})


class VerifySmsView(View):
    def post(self, request):
        verify_sms_form = VerifySmsForm(request.POST)
        if verify_sms_form.is_valid():
            # 用户输入的验证码正确。允许修改密码
            activate_code = save_email_verify_record(verify_sms_form.data["mobile"], "forget")
            return redirect(reverse("reset_password", kwargs={"activate_code": activate_code}))
        else:
            return render(request, "verify_sms.html", {"verify_sms": verify_sms_form})

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
            user = UserProfile.objects.get(Q(email=email)|Q(mobile_phone=email))
            user.password = make_password(password)
            user.is_active = True
            user.save()

            # 删除该用户的所有的激活链接
            EmailVerifyRecord.objects.filter(email=email).delete()
            return render(request, "user_login.html", {
                "login_title": "密码修改成功。请重新登录。"
            })
        else:
            email = request.POST.get("email", "")
            return render(request, "password_reset.html", {"email":email, "reset_form":modify_form})
