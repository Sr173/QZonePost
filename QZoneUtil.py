import requests
import re
import base64

def getGTK(skey):
    hash = 5381
    for i in range(0,len(skey)):
        hash += (hash << 5) + utf8_unicode(skey[i])
    return hash & 0x7fffffff

def utf8_unicode(c):
    if len(c)==1:
        return ord(c)
    elif len(c)==2:
        n = (ord(c[0]) & 0x3f) << 6
        n += ord(c[1]) & 0x3f
        return n
    elif len(c)==3:
        n = (ord(c[0]) & 0x1f) << 12
        n += (ord(c[1]) & 0x3f) << 6
        n += ord(c[2]) & 0x3f
        return n
    else:
        n = (ord(c[0]) & 0x0f) << 18
        n += (ord(c[1]) & 0x3f) << 12
        n += (ord(c[2]) & 0x3f) << 6
        n += ord(c[3]) & 0x3f
        return n

class QZoneUtil:
    __qzone_token = ''
    __uin = ''
    __session = requests.session()
    __gtk = ''

    def __init__(self, uin):
        headers = {
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }
        self.__session.headers = headers
        self.__uin = uin

    def login(self, client_key):
        self.__session.get(
            "https://ui.ptlogin2.qq.com/cgi-bin/login?pt_hide_ad=1&style=9&appid=549000929&pt_no_auth=1&pt_wxtest=1&daid=5&s_url=https%3A%2F%2Fh5.qzone.qq.com%2Fmqzone%2Findex")
        self.__session.cookies["pgv_pvi"] = "4891808768"
        self.__session.cookies["pgv_si"] = "s3110396928"
        login_url = "https://ssl.ptlogin2.qq.com/jump?u1=https%3A%2F%2Fh5.qzone.qq.com%2Fmqzone%2Findex&pt_report=1&daid=5&style=9&pt_ua=30F0FC03C9EEBCDCF868871DF5F9648D&pt_browser=MQQBrowser&keyindex=19&clientuin=" + self.__uin + "&clientkey=" + client_key
        login_result = self.__session.get(login_url)
        home_page = self.__session.get("https://h5.qzone.qq.com/mqzone/index")
        self.__qzone_token = re.search(r'window\.g_qzonetoken = \(function\(\)\{ try\{return (.*?);\} catch\(e\)',
                                       home_page.text)
        if not self.__qzone_token:
            return False
        self.__qzone_token = self.__qzone_token.group(1)
        skey = self.__session.cookies['p_skey']
        self.__gtk = getGTK(skey)
        return True

    def post_shuoshuo(self, con, pic_list):
        reqURL = 'https://user.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_publish_v6??g_tk={0}&qzonetoken={1}'.format(
            self.__gtk, self.__qzone_token)
        data = (
            ('syn_tweet_verson', '1'),
            ('paramstr', '1'),
            ('pic_template', ''),
            ('richtype', '1' if len(pic_list) > 0 else ''),
            ('richval', pic_list[0]),
            ('special_url', ''),
            ('subrichtype', ''),
            ('who', '1'),
            ('con', con),
            ('ver', '1'),
            ('ugc_right', '1'),
            ('to_sign', '1'),
            ('hostuin', self.__uin),
            ('code_version', '1'),
            ('format', 'fs'),
            ('qzreferrer', 'https://user.qzone.qq.com/6645815'),
        )

        rsp = self.__session.post(reqURL, data=data)
        print(rsp)


