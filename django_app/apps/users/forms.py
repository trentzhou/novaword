# -*- coding: utf-8 -*-
import json

from django import forms
from captcha.fields import CaptchaField

from utils.wilddog_sms import SmsClient
from word_master.settings import WILDDOG_APP_ID, WILDDOG_API_KEY
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
            c = SmsClient(WILDDOG_APP_ID, WILDDOG_API_KEY)
            result = c.check_code(self.data['mobile'], self.data['verification_code'])
            verification_good = False
            try:
                result = json.loads(result)
                if result["status"] == "ok":
                    verification_good = True
            except:
                verification_good = False
            if not verification_good:
                self.add_error("verification_code", u"验证码错误")
        return super(RegisterMobileForm, self).is_valid()


class VerifySmsForm(forms.Form):
    mobile = forms.IntegerField(required=True)
    code = forms.IntegerField(required=True)

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
