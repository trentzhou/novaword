# -*- coding: utf-8 -*-
from django import forms
from captcha.fields import CaptchaField

from .models import UserProfile

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


class ForgetForm(forms.Form):
    email = forms.EmailField(required=True)
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
