import QZoneUtil
import execjs

def get_js():
    # f = open("D:/WorkSpace/MyWorkSpace/jsdemo/js/des_rsa.js",'r',encoding='UTF-8')
    f = open("./c_login_2.js", 'r', encoding='UTF-8')
    line = f.readline()
    htmlstr = ''
    while line:
        htmlstr = htmlstr + line
        line = f.readline()
    return htmlstr

jsstr = get_js()
print(execjs.get().name)
ctx = execjs.compile(jsstr)

qzone = QZoneUtil.QZoneUtil('1301485673')

# aid = '522005705'
# daid = '4'

aid = '21000124'
daid = '8'

vsig, tk = qzone.check_user_need_vcode(aid, daid)
pk = qzone.deal_slider_vcode(aid, vsig)

print('vsig', vsig)

tick = pk['data']['data']['ticket']
rand_str = pk['data']['data']['randstr']
print('tk', tk)

p = ctx.call('getPwd', 'zxj13789035505', '1301485673', rand_str)
lr = qzone.login(aid, daid, p, rand_str, tick, tk)

img = qzone.upload_image("./ve.jpg")
qzone.post_shuoshuo('qm协议测试 https://caohua.com/', [img])