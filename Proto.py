import base64
import json
from io import BytesIO
import time
import random

import requests

class Util:
    __host = ''
    __session_id = ''



    def __init__(self, host='http://localhost:808', proxy=''):
        self.__host = host
        data = {

            'device': {
                'AndroidId': 'c0e66cdeb42a7' + str(random.randint(100, 999)),
                'Mac': '02:00:00:00:00:00',
                'OsType': 'android',
                'OsVersion': '7.1.2',
                'SimName': 'China Mobile GSM',
                'MobileBrand': 'vivo',
                'MobileModel': 'x6',
                'WifiName': 'ILoveYou',
                'WifiSSID': '+T+kZS5QKCu23yGqWj1u+g==',
                'IMEI': '865166022738994',
                'IMSI': ''
            },

            'app': {
                'PakName': 'com.tencent.mobileqq',
                'QQAppSig': 'prdFvySiwndSdxb28262jQ==',
                'AppVer': '8.2.0',
                'ClientVersion': '8.2.0.27f6ea96',
                'AppId': 16
            }
        }

        if proxy != '':
            data['Sk5'] = {
                'Host': proxy
            }

        session_result = requests.post(
            host + "/v1/Session", json=data
        )

        session_data = json.loads(session_result.content)
        self.__session_id = session_data["data"]["SessionId"]

    def login(self, qq, pwd):
        user_json = {
            "QQNumber": qq,
            "PwdType": 0,
            "Pwd": pwd
        }

        login_result_resp = requests.post(
            self.__host + "/v1/Login?id=" + str(self.__session_id),
            data=json.dumps(user_json)
        )

        login_result = json.loads(login_result_resp.content)

        while login_result['data']['Result'] == 2:
            print("正在输入验证码")
            pic = base64.b64decode(login_result['data']['VCode'])
            io = BytesIO(pic)
            v_code = requests.post("http://119.23.8.232/v1/detect", data=io)
            login_result = requests.post(self.__host + "/v1/VCode?id=" + str(self.__session_id), data=json.dumps({
                'VCode': v_code.text
            })).text
            login_result = json.loads(login_result)

        return login_result
