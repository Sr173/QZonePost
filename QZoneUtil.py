import json

import requests
import re
import base64
import os

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

    def __init__(self, uin, proxy=''):
        headers = {
            'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }
        self.__session.headers = headers
        # self.__session.proxies = {
        #     'http': 'socks5://' + proxy,
        #     'https': 'socks5://' + proxy
        # }
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
        self.__qzone_token = self.__qzone_token.strip('"')

        skey = self.__session.cookies['p_skey']
        self.__gtk = getGTK(skey)
        return True

    def post_shuoshuo(self, con, pic_list):
        reqURL = 'https://user.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_publish_v6??g_tk={0}&qzonetoken={1}'.format(
            self.__gtk, self.__qzone_token)

        richval = ''

        for i in pic_list:
            richval = richval + i + ' '


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
            ('qzreferrer', 'https://user.qzone.qq.com/' + self.__uin),
        )

        rsp = self.__session.post(reqURL, data=data)
        print(rsp)

    def upload_image(self, path):
        file = open(path, 'rb')
        file_content = file.read()
        file.close()
        base64_pic = base64.urlsafe_b64encode(file_content)


        reqURL = 'https://up.qzone.qq.com/cgi-bin/upload/cgi_upload_image?g_tk={0}&qzonetoken={1}&g_tk={2}'.format(
            self.__gtk, self.__qzone_token, self.__gtk)
        data = (
            ('filename', 'filename'),
            ('uin', self.__uin),
            ('skey', self.__session.cookies['skey']),
            ('zzpaneluin', self.__uin),
            ('zzpanelkey', ''),
            ('p_uin', self.__uin),
            ('p_skey', self.__session.cookies['p_skey']),
            ('qzonetoken', self.__qzone_token),
            ('uploadtype', '1'),
            ('albumtype', '7'),
            ('exttype', '0'),
            ('refer', 'shuoshuo'),
            ('output_type', 'json'),
            ('charset', 'utf-8'),
            ('output_charset', 'utf-8'),
            ('upload_hd', '1'),
            ('hd_width', '2048'),
            ('hd_height', '10000'),
            ('hd_quality', '96'),
            ('backUrls', 'http://upbak.photo.qzone.qq.com/cgi-bin/upload/cgi_upload_image,http://119.147.64.75/cgi-bin/upload/cgi_upload_image'),
            ('url', 'https://up.qzone.qq.com/cgi-bin/upload/cgi_upload_image?g_tk=' + str(self.__gtk)),
            ('base64', '1'),
            ('jsonhtml_callback', 'callback'),
            ('picfile', base64_pic),
            ('qzreferrer', 'https://user.qzone.qq.com/' + self.__uin),
        )

        rsp = self.__session.post(reqURL, data=data)

        if rsp.content == '':
            return ''

        result = rsp.content[10: -3]
        result = json.loads(result)

        if result['ret'] != 0:
            return ''

        img = ',' + result['data']['albumid'] + ',' + result['data']['lloc'] + ',' + result['data']['lloc'] + ',' + str(result['data']['type'])
        img = img + ',' + str(result['data']['height']) + ',' + str(result['data']['width'])
        img = img + ',,' + str(result['data']['height']) + ',' + str(result['data']['width'])

        return img