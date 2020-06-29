# -*- coding: utf-8 -*-
__author__ = 'bobby'
__date__ = '2016/10/30 22:11'
from random import Random

import os

if os.getenv("DISABLE_SMTP", None):
    # SMTP is disabled, we need to use HTTP to send mail

    # 发邮件的服务。因为aws不允许连接到smtp服务器，所以我试用了 sendcloud.net 来发送邮件。
    def send_mail(title, body, email_from, email_to):
        """
        Send a mail using service provided by sendcloud.net.
        The interface is identical to django.core.mail#send_mail.

        :param str title: mail title
        :param str body: mail body
        :param str email_from: mail from
        :param list email_to: recipients
        :return None:
        """
        url = "http://api.sendcloud.net/apiv2/mail/send"

        # 您需要登录SendCloud创建API_USER，使用API_USER和API_KEY才可以进行邮件的发送。
        params = {
            "apiUser": "word_master_test_XW4ZqJ",
            "apiKey": "oqQ8UN2BCa5utxRH",
            "from": "service@sendcloud.im",
            "fromName": email_from,
            "to": email_to,
            "subject": title,
            "html": body
        }

        requests.post(url, files={}, data=params)
        return True

else:
    from django.core.mail import send_mail
import requests
import json
from users.models import EmailVerifyRecord
from django.conf import settings


def random_str(randomlength=8):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str+=chars[random.randint(0, length)]
    return str



def save_email_verify_record(email, send_type):
    email_record = EmailVerifyRecord()
    if send_type == "update_email":
        code = random_str(4)
    else:
        code = random_str(16)
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save()
    return code


def send_register_email(email, send_type="register", base_url="http://localhost:8000"):
    code = save_email_verify_record(email, send_type)

    email_title = ""
    email_body = ""

    if send_type == "register":
        email_title = "Nova背单词 -- 注册激活链接"
        email_body = "请点击下面的链接激活你的账号: {0}/activate/{1}".format(base_url, code)

        send_status = send_mail(email_title, email_body, settings.EMAIL_FROM, [email])
        if send_status:
            pass
    elif send_type == "forget":
        email_title = "Nova背单词 -- 注册密码重置链接"
        email_body = "请点击下面的链接重置密码: {0}/reset_password/{1}".format(base_url, code)

        send_status = send_mail(email_title, email_body, settings.EMAIL_FROM, [email])
        if send_status:
            pass
    elif send_type == "update_email":
        email_title = "Nova背单词 -- 邮箱修改验证码"
        email_body = "你的邮箱验证码为: {0}".format(code)

        send_status = send_mail(email_title, email_body, settings.EMAIL_FROM, [email])
        if send_status:
            pass


