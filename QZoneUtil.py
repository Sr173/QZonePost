import json
import urllib
import requests
import re
import base64
import os
import time

HOST = 'https://cf.qq.com'

def getmidstring(html, start_str, end):
    start = html.find(start_str)
    if start >= 0:
        start += len(start_str)
        end = html.find(end, start)
        if end >= 0:
            return html[start:end].strip()

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
            'user-agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3704.400 QQBrowser/10.4.3587.400',
            'Refer': 'https://xui.ptlogin2.qq.com/cgi-bin/xlogin?appid=523005419&style=42&s_url=http://wtlogin.qq.com/&daid=120&pt_no_auth=1'
        }
        self.__session.headers = headers



        if proxy != '':
            self.__session.proxies = {
                'http': 'socks5://' + proxy,
                'https': 'socks5://' + proxy
            }

        self.__uin = uin

    def check_user_need_vcode(self, aid, daid):
        qzone_url = 'https://xui.ptlogin2.qq.com/cgi-bin/xlogin?target=self&appid=' + aid + '&daid=' + daid +'&s_url=https://mail.qq.com/cgi-bin/readtemplate?check=false%26t=loginpage_new_jump%26vt=passport%26vm=wpt%26ft=loginpage%26target=&style=25&low_login=1&proxy_url=https://mail.qq.com/proxy.html&need_qr=0&hide_border=1&border_radius=0&self_regurl=http://zc.qq.com/chs/index.html?type=1&app_id=11005?t=regist&pt_feedback_link=http://support.qq.com/discuss/350_1.shtml&css=https://res.mail.qq.com/zh_CN/htmledition/style/ptlogin_input24e6b9.css'
        print (qzone_url)
        resp = self.__session.get(qzone_url)

        self.__session.get("https://xui.ptlogin2.qq.com/cgi-bin/xlogin?target=self&appid=" + aid + "&daid=" + daid + "&s_url=https://mail.qq.com/cgi-bin/readtemplate?check=false%26t=loginpage_new_jump%26vt=passport%26vm=wpt%26ft=loginpage%26target=&style=25&low_login=1&proxy_url=https://mail.qq.com/proxy.html&need_qr=0&hide_border=1&border_radius=0&self_regurl=http://zc.qq.com/chs/index.html?type=1&app_id=11005?t=regist&pt_feedback_link=http://support.qq.com/discuss/350_1.shtml&css=https://res.mail.qq.com/zh_CN/htmledition/style/ptlogin_input24e6b9.css")

        text = resp.text
        js_ver = getmidstring(text, 'ptui_version:encodeURIComponent("', '"')
        print(self.__session.cookies)
        login_sig = self.__session.cookies['pt_login_sig']
        check_param = {
            "regmaster": "",
            "pt_tea": "2",
            'pt_vcode': '1',
            'uin': self.__uin,
            'appid': aid,
            'js_ver': js_ver,
            'js_type': '1',
            'login_sig': login_sig,
            'u1': HOST,
            'r': '0.27872559952975506',
            'pt_uistyle': '25'
        }

        cookie = {}
        for k in self.__session.cookies:
            cookie[k.name] = k.value

        cp = urllib.parse.urlencode(check_param)
        cp = urllib.parse.unquote(cp)
        print(cp)
        resp = self.__session.get('https://ssl.ptlogin2.qq.com/check?' + cp, cookies=cookie)
        print(resp.text)
        cap = re.findall("'(.*?)'", resp.text, re.M)
        print(cap[5])
        return cap[1], cap[5]

    def deal_slider_vcode(self, aid, tk):
        vcode_info = json.dumps({
            'appid': int(aid),
            'capcd': tk,
            'qq': self.__uin
        }, separators=(',', ':'))

        print(vcode_info)
        data = {
            'id': '9878',
            'dev_id': '',
            'token': '5058621957c8a804056f2d43455b7859',
            'type': 'tx_qq',
            'data': vcode_info
        }

        deal_data = urllib.parse.urlencode(data)
        deal_data = urllib.parse.unquote(deal_data)

        print(deal_data)

        str = requests.post('http://www.qieocr.com/qieocr', data=data)
        print(str.text)
        ret_id = json.loads(str.text)
        task_id = ret_id['data']['id']
        print(task_id)
        time.sleep(3)
        data = {
            'uid': '9878',
            'token': '5058621957c8a804056f2d43455b7859',
            'tid': task_id
        }

        resp = requests.post('http://www.qieocr.com/getdata', data=data)
        print(resp.text)
        return json.loads(resp.text)

    def login(self, aid, daid , p, vcode, tick, tk):
        login_sig = self.__session.cookies['pt_login_sig']

        #https://ssl.ptlogin2.qq.com/login?
        # u=66456804
        # &verifycode=@09C
        # &pt_vcode_v1=1
        # &pt_verifysession_v1=t02_mMV10uX-jgCeH8fkHtZBCRclCtmHjRPkmpP234xgVHaO3gDpOFJ3tRrxGhTnoD5qYKZtunWiE9sfGyh4ZJ-m1sWDKvV8b59iLtteKNDqdF774VrVe-Y2g**
        # &p=kToWdZkQZ1Oc2U9Us9TlsRtG*dLe2rUW5*wJe1fLafiOJqB57CDrtEzSnNPj3a7BfNCFo5bcBkfsWrspvO1qPWP3CFMAoEDFvZifNmfdPtMGqqnMcBnEOkePvtTZDxnQCxlF3dSbhD7xORW*P2k7A*z3PubyFu-UhmzSZaWUmIY46jOFZ4StS8rRQFzqj64uv3NGdnorbxvAizaHIRskW380Em2h0nOfIgUq1XrVbymm7M6v6Y3kXZh8omy*pSMpLEAUO6kJ01K3GGwOa90887B6GVHWhaKet7T5LNQbd6cnbsSJe5OQb-sffOcVSsovTx25LJOFWkb6KDjWKbX2Cg__
        # &pt_randsalt=2
        # &u1=https://qzone.qq.com
        # &ptredirect=0
        # &h=1
        # &t=1
        # &g=1
        # &from_ui=1
        # &ptlang=2052
        # &action=8-4-1564394896571
        # &js_ver=19062020
        # &js_type=1
        # &login_sig=8InXwbqkCL3uLAZfManxwh-1MWr4TGgCV758A-puzUUj8v4dayXzcsXVjvyz4H2g
        # &pt_uistyle=25
        # &aid=549000912
        # &daid=5
        # &ptdrvs=uVNsQcZ6mHTjMQb6IPmien3j1P6tYWZ5xZYrbvDP9rDV80b-C17kDkv1hot5-QrYmMe6F0SrTws_&

        login_param = {
            'u': self.__uin,
            "verifycode": vcode,
            'pt_vcode_v1': 1,
            'pt_verifysession_v1': tick,
            'p': p,
            'pt_randsalt': 2,
            'u1': HOST,
            'ptredirect': '0',
            'from_ui': '1',
            'h': '1',
            't': '1',
            'g': '1',
            'ptlang': '2052',
            'action': '8-4-1564394896571',
            'js_ver': '19062020',
            'js_type': '1',
            'login_sig': login_sig,
            'pt_uistyle': 25,
            'aid': aid,
            'daid': daid,
            'ptdrvs': tk
        }


        lp = urllib.parse.urlencode(login_param)
        lp = urllib.parse.unquote(lp)
        url = 'https://ssl.ptlogin2.qq.com/login?' + lp + '&'
        print(url)
        resp = self.__session.get(url)
        print(resp.text)
        cap = re.findall("'(.*?)'", resp.text, re.M)
        url = cap[2]
        print(url)
        pt_sigx = getmidstring(url, 'ptsigx=', '&')

        url = 'https://ptlogin2.qzone.qq.com/check_sig?pttype=1&uin=' + str(self.__uin) + \
              '&service=login&nodirect=0&ptsigx=' + pt_sigx + "&s_url=" + "https://qzs.qq.com" + "&f_url=&ptlang=2052&ptredirect=100" \
              "&aid=" + '549000912' + "&daid=" + '5' + "&j_later=0&low_login_hour=0&regmaster=0&pt_login_type=1&pt_aid=0&pt_" \
                                                "aaid=0&pt_light=0&pt_3rd_aid=0"
        resp = self.__session.get(url, allow_redirects=False)
        print(resp.text)
        print(self.__session.cookies)
        resp = self.__session.get('https://h5.qzone.qq.com/mqzone/index')
        print(self.__session.cookies)
        print(resp.text)
        return


    def login_with_clientkey(self, client_key):
        self.__session.get(
            "https://ui.ptlogin2.qq.com/cgi-bin/login?pt_hide_ad=1&style=9&appid=549000929&pt_no_auth=1&pt_wxtest=1&daid=5&s_url=https%3A%2F%2Fh5.qzone.qq.com%2Fmqzone%2Findex")
        self.__session.cookies["pgv_pvi"] = "4891808758"
        self.__session.cookies["pgv_si"] = "s3110396918"
        login_url = "https://ssl.ptlogin2.qq.com/jump?u1=https%3A%2F%2Fh5.qzone.qq.com%2Fmqzone%2Findex&pt_report=1&daid=5&style=9&pt_ua=30F0FD03C9EEBCDCF868871DF5F9648D&pt_browser=MQQBrowser&keyindex=19&clientuin=" + self.__uin + "&clientkey=" + client_key
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