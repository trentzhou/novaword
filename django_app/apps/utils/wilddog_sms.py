import requests
import time
import hashlib

NOTIFY_SEND_URL = "https://sms.wilddog.com/api/v1/{}/notify/send"
CODE_SEND_URL = "https://sms.wilddog.com/api/v1/{}/code/send"
CODE_CHECK_URL = "https://sms.wilddog.com/api/v1/{}/code/check"
STATUS_URL = "https://sms.wilddog.com/api/v1/{}/status?"
BALANCE_URL = "https://sms.wilddog.com/api/v1/{}/getBalance?"

headers = {
    "User-Agent": "wilddog-sms-python/1.0.1"
}


class SmsClient:
    def __init__(self, appid, smskey):
        self.appid = appid
        self.smskey = smskey

    def _signature(self, request_body):
        sign_param = sorted(request_body.items(), key=lambda d: d[0])
        sign_source = ""
        for i in sign_param:
            sign_source = sign_source + i[0] + "=" + i[1] + "&"
        sign_source = sign_source + self.smskey
        sign = hashlib.sha256(sign_source).hexdigest()
        return sign

    def send_code(self, mobile, templateId, params):
        if type(params) is None:
            request_body = {"templateId": templateId, "mobile": mobile, "timestamp": "%d" % (time.time() * 1000),
                            "params": params}
        else:
            request_body = {"templateId": templateId, "mobile": mobile, "timestamp": "%d" % (time.time() * 1000)}
        sign = self._signature(request_body)
        request_body['signature'] = sign
        r = requests.post(url=CODE_SEND_URL.format(self.appid), data=request_body, headers=headers)
        if r.status_code == 200 or r.status_code == 400 or r.status_code == 500:
            return r.text
        return r

    def send_notify(self, mobiles, templateId, params):
        request_body = {"templateId": templateId, "mobiles": mobiles, "timestamp": "%d" % (time.time() * 1000),
                        "params": params}
        sign = self._signature(request_body)
        request_body['signature'] = sign
        r = requests.post(url=NOTIFY_SEND_URL.format(self.appid), data=request_body, headers=headers)
        if r.status_code == 200 or r.status_code == 400 or r.status_code == 500:
            return r.text
        return r

    def check_code(self, mobile, code):
        request_body = {"mobile": mobile, "code": code, "timestamp": "%d" % (time.time() * 1000)}
        sign = self._signature(request_body)
        request_body['signature'] = sign
        r = requests.post(url=CODE_CHECK_URL.format(self.appid), data=request_body, headers=headers)
        if r.status_code == 200 or r.status_code == 400 or r.status_code == 500:
            return r.text
        return r

    def query_status(self, rrid):
        request_body = {"rrid": rrid}
        sign = self._signature(request_body)
        request_body['signature'] = sign
        r = requests.get(url=STATUS_URL.format(self.appid), params=request_body, headers=headers)
        if r.status_code == 200 or r.status_code == 400 or r.status_code == 500:
            return r.text
        return r

    def query_balance(self):
        requestBody = {"timestamp": "%d" % (time.time() * 1000)}
        sign = self._signature(requestBody)
        requestBody['signature'] = sign
        r = requests.get(url=BALANCE_URL.format(self.appid), params=requestBody, headers=headers)
        if r.status_code == 200 or r.status_code == 400 or r.status_code == 500:
            return r.text
        return r

def is_valid_phone_number(mobile):
    """
    Check whether a phone number is valid
    :param str mobile: phone number
    :return bool:
    """
    if mobile.isdigit() and len(mobile) == 11:
        return True
    return False