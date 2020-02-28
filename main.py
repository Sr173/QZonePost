import QZoneUtil
import Proto
import pickle
import time
import fileinput
import os.path
import requests

def get_client_key(qq, pwd, proxy=''):
    proto = Proto.Util("http://localhost:808", proxy)
    result = proto.login(qq, pwd)

    if result['status'] != 0:
        print("登陆失败[{0}]".format(qq), result['status'], result['message'])
        return ''

    if result['data']['Result'] != 0 or result['data']['SKey'] == '':
        print("登陆失败[{0}]".format(qq), result['data']['ErrMsg'])
        return ''

    print('登陆成功')
    client_key = result['data']['ClientKey']
    return client_key

client_key_list = {}

if os.path.isfile("client.key"):
    with open("client.key", "rb") as f:
        client_key_list = pickle.load(f)
    f.close()

for line in fileinput.input("qq.txt"):
    try:
        line = line.strip('\n')
        line = line.strip('\r')
        data = str(line).split('----')
        if data.__len__() == 2:
            proxy = requests.get(
               'http://ip.11jsq.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=0&fa=0&fetch_key'
               '=&groupid=0&qty=1&time=1&pro=&city=&port=2&format=txt&ss=3&css=&dt=1&specialTxt=3&specialJson'
               '=&usertype=14')
            time.sleep(1)
            proxy_text = proxy.text.strip('\n')

            is_new = False

            if data[0] in client_key_list:
                client_key = client_key_list[data[0]]
            else:
                client_key = get_client_key(int(data[0]), data[1], proxy=proxy_text)
                is_new = True

            if client_key == '':
                continue

            qzone = QZoneUtil.QZoneUtil(data[0], proxy_text)
            login_result = qzone.login(client_key)



            if not is_new and login_result == False:
                client_key = get_client_key(int(data[0]), data[1], proxy=proxy_text)
                is_new = True
                login_result = qzone.login(client_key)
                if client_key == '':
                    continue

            if is_new:
                client_key_list[data[0]] = client_key
                with open("client.key", "wb") as f:
                    pickle.dump(client_key_list, f)
                f.close()

            img = qzone.upload_image("./vc.png")

            print(img)
            qzone.post_shuoshuo('qm你好，可以看一下', [img, img])
        else:
            print("格式错误")
    except Exception as e:
        print("发生了异常", e)


