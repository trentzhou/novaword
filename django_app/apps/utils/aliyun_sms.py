import json

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from django.conf import settings
import random

from users.models import SmsVerifyRecord


class AliyunSms(object):
    MSG_TYPE_REGISTER = "register"
    MSG_TYPE_FORGET = "forget"

    def __init__(self):
        accessKey = settings.ALIYUN_ACCESS_KEY
        accessSecret = settings.ALIYUN_ACCESS_SECRET
        self.sign_name = settings.ALIYUN_SIGN_NAME
        self.aliyun_client = AcsClient(accessKey, accessSecret, 'cn-hangzhou')

    def send_sms(self, phone_number, msg_type, code=0):
        if code == 0:
            code = self.generate_code()
        if msg_type == AliyunSms.MSG_TYPE_REGISTER:
            template_code = 'SMS_164075985'
        else:
            template_code = 'SMS_164075981'
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https')  # https | http
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')

        request.add_query_param('RegionId', 'cn-hangzhou')
        request.add_query_param('PhoneNumbers', phone_number)
        request.add_query_param('SignName', self.sign_name)
        request.add_query_param('TemplateCode', template_code)
        request.add_query_param('TemplateParam', json.dumps({ "code": code }))

        try:
            response = self.aliyun_client.do_action_with_exception(request)
            result = json.loads(str(response, encoding="utf-8"))
            if result["Code"] == "OK":
                # save the send record
                record = SmsVerifyRecord()
                record.code = code
                record.send_type = msg_type
                record.mobile_phone = phone_number
                record.save()
        except:
            return None

    def generate_code(self):
        code = random.randint(1000, 9999)
        return code

    def check_code(self, mobile, code):
        found = SmsVerifyRecord.objects.filter(mobile_phone=mobile, code=code).count()
        # delete all records for the phone
        SmsVerifyRecord.objects.filter(mobile_phone=mobile).delete()
        if found:
            return True
        return False

