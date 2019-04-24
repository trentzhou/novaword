# -*- coding: utf-8 -*-
import json

from django import forms
from captcha.fields import CaptchaField

from utils.aliyun_sms import AliyunSms
from django.conf import settings
from .models import UserProfile, EmailVerifyRecord


class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, min_length=5)


class RegisterForm(forms.Form):
    nickname = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=5)
    password_confirm = forms.CharField(required=True, min_length=5)
    captcha = CaptchaField(error_messages={"invalid": u"验证码错误"})

    def is_valid(self):
        if self.is_bound:
            if self.data['password'] != self.data['password_confirm']:
                self.add_error("password_confirm", u"密码不一致")
        return super(RegisterForm, self).is_valid()


class RegisterMobileForm(forms.Form):
    nickname = forms.CharField(required=True)
    mobile = forms.IntegerField(required=True)
    password = forms.CharField(required=True, min_length=5)
    password_confirm = forms.CharField(required=True, min_length=5)
    verification_code = forms.IntegerField(required=True)

    def is_valid(self):
        if self.is_bound:
            if self.data['password'] != self.data['password_confirm']:
                self.add_error("password_confirm", u"密码不一致")
            # check verification code
            c = AliyunSms()
            result = c.check_code(self.data['mobile'], self.data['verification_code'])
            verification_good = result
            if not verification_good:
                self.add_error("verification_code", u"验证码错误")
        return super(RegisterMobileForm, self).is_valid()


class VerifySmsForm(forms.Form):
    mobile = forms.IntegerField(required=True)
    code = forms.IntegerField(required=True)

    def is_valid(self):
        # check verification code
        c = AliyunSms()
        verification_good = c.check_code(self.data['mobile'], self.data['code'])
        if not verification_good:
            self.add_error("code", u"验证码错误")
        return super(VerifySmsForm, self).is_valid()


class ForgetForm(forms.Form):
    email = forms.CharField(required=True)
    captcha = CaptchaField(error_messages={"invalid": u"验证码错误"})


class ModifyPasswordForm(forms.Form):
    password = forms.CharField(required=True, min_length=5)
    password_confirm = forms.CharField(required=True, min_length=5)

    def is_valid(self):
        if self.is_bound:
            if self.data['password'] != self.data['password_confirm']:
                self.add_error("password_confirm", u"密码不一致")
        return super(ModifyPasswordForm, self).is_valid()


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar']


class AjaxChangeNickNameForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['nick_name']


class AjaxGetEmailVerificationForm(forms.Form):
    email = forms.EmailField(required=True)


class AjaxUpdateEmailForm(forms.Form):
    email = forms.EmailField(required=True)
    verification_code = forms.CharField(required=True)

    def is_valid(self):
        query = EmailVerifyRecord.objects.filter(email=self.data["email"], code=self.data["verification_code"])
        if not query.count():
            self.add_error("verification_code", u"验证码错误")
        return super(AjaxUpdateEmailForm, self).is_valid()


class AjaxChangePasswordForm(forms.Form):
    old_password = forms.CharField(required=True)
    password = forms.CharField(required=True)
    confirm_password = forms.CharField(required=True)

    def is_valid(self):
        if self.data["password"] != self.data["confirm_password"]:
            self.add_error("confirm_password", u"密码不一致")
        return super(AjaxChangePasswordForm, self).is_valid()
