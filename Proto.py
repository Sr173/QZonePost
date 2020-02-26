import base64
import json
from io import BytesIO

import requests

class Util:
    __host = ''
    __session_id = ''

    def __init__(self, host='http://localhost:808'):
        self.__host = host

        session_result = requests.post(
            host + "/v1/Session",
            data="{\n\"device\" : {\r\n    \"AndroidId\":\"c0e66cdfb42a71e7\",\r\n    \"Mac\":\"02:00:00:00:00:00\","
                 "\r\n    \"OsType\":\"android\",\r\n    \"OsVersion\":\"7.1.2\",\r\n    \"SimName\":\"China Mobile "
                 "GSM\",\r\n    \"MobileBrand\":\"vivo\",\r\n    \"MobileModel\":\"vivo x6plus d\","
                 "\r\n    \"WifiName\":\"ILoveYou\",\r\n    \"WifiSSID\":\"+T+kZS5QKCu23yGqWj1u+g==\","
                 "\r\n    \"IMEI\":\"865166022738994\",\r\n    \"IMSI\":\"460007201665705\"},\r\n\r\n\"app\" : {\r\n  "
                 "      \"PakName\":\"com.tencent.mobileqq\",\r\n        \"QQAppSig\":\"prdFvySiwndSdxb28262jQ==\","
                 "\r\n        \"AppVer\":\"8.2.0\",\r\n        \"ClientVersion\":\"8.2.0.27f6ea96\",\r\n        "
                 "\"AppId\":16\r\n    }\r\n} "
        )

        session_data = json.loads(session_result.content)
        self.__session_id = session_data["data"]["SessionId"]

    def login(self, qq, pwd):
        user_json = {
            "QQNumber": 6645815,
            "PwdType": 0,
            "Pwd": "fan147147"
        }

        login_result_resp = requests.post(
            "http://119.23.8.232:808/v1/Login?id=" + str(self.__session_id),
            data=json.dumps(user_json)
        )

        login_result = json.loads(login_result_resp.content)

        while login_result['data']['Result'] == 2:
            print("需要验证码")
            pic = base64.b64decode(login_result['data']['VCode'])
            io = BytesIO(pic)
            v_code = requests.post("http://119.23.8.232/v1/detect", data=io)
            login_result = requests.post("http://119.23.8.232:808/v1/VCode?id=" + str(self.__session_id), data=json.dumps({
                'VCode': v_code.text
            })).text
            login_result = json.loads(login_result)

        return login_result
