import requests
from time import time
from urllib import parse
from base64 import b64encode


class Login():
    def __init__(self,username,password):
        self.sess = requests.session()
        self.username = username
        self.passward = password
        self.headers = {
            'Referer': 'https://weibo.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36 Edg/86.0.622.38'
        }
    def get_pubkey(self):
        url = 'https://login.sina.com.cn/sso/prelogin.php'
        su = b64encode(parse.quote(self.username).encode('utf8')).decode('utf8')
        params = {
            'entry': 'weibo',
            #'callback': 'sinaSSOController.preloginCallBack',
            'su': su,
            'rsakt': 'mod',
            'checkpin': '1',
            'client': 'ssologin.js(v1.4.19)',
            '_': round(time()*1000)
        }
        try:
            response = self.sess.get(url=url,headers=self.headers,params=params)
            print(response.text)
            return response
        except Exception:
            print('获取公钥失败。')

login = Login('15827477139','aaa')
login.get_pubkey()

