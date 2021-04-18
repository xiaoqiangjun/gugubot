"""
# Author: Xiaoqiangjun
# Date: 2021-04-15 11:08:06
# LastEditTime: 2021-04-18 22:38:24
# LastEditors: Xiaoqiangjun
# FilePath: /gugubot/login.py
"""

import logging
import logging.config
import pickle
import sys
from binascii import b2a_hex
from base64 import b64encode
from json import loads, load
from random import random
from time import time
from urllib import parse
from os import listdir

import requests
import rsa


class Login:
    """
    定义微博登录流程，包括获取公钥，预登录与登录
    """
    def __init__(self, username, password, token=None, cookies_flag=True):
        """
         # description: 初始化用户名，密码，ocr密钥
         # param int/str username 用户名、邮箱、手机号等
         # param str password 密码
         # param str token 快识平台 fast.95man.com 验证码识别令牌
         # param bool cookies_flag 是否尝试使用以保存的cookies登录
         # return None
        """

        self.sess = requests.session()
        self.username = str(username)
        self.password = str(password)
        self.ocr_token = str(token)
        self.cookies_flag = cookies_flag
        self._setup_logging(default_path="log.json")
        # 用户名base64编码
        self.su = b64encode(parse.quote(self.username).encode('utf8')).decode('utf8')
        self.headers = {
            'Referer':
            'https://mail.sina.com.cn/',
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36 Edg/86.0.622.38'
        }

    def _setup_logging(self, default_path="log.json", default_level=logging.INFO):
        try:
            with open(default_path, "r") as f:
                logging.config.dictConfig(load(f))
        except IOError:
            logging.basicConfig(level=default_level)
            logging.error("日志配置文件不存在请检查log/log.json文件！", exc_info=True)

    def get_pubkey(self):
        """
        # description: 获取登录公钥等，用于加密密码登录
        # param None
        # return dict response
        # 请求链接：https://login.sina.com.cn/sso/prelogin.php?rsakt=mod&client=ssologin.js(v1.4.19)
        # 一个返回示例：
        {
            'retcode': 0,
            'servertime': 1618476658,
            'pcid': 'tc-57a394c85361e16cf311bbaa06836ce1efa9',
            'nonce': '841DCW',
            'pubkey': 'EB2A382313...256位...4A799B3181D6442443',
            'rsakv': '1330428213',
            'is_openlock': 0,
            'exectime': 42
        }
        """

        url = 'https://login.sina.com.cn/sso/prelogin.php?rsakt=mod&client=ssologin.js(v1.4.19)'
        params = {
            # 非必要的固定参数写在了url里
            'entry': 'weibo',
            'su': self.su,
            '_': round(time() * 1000)
        }
        response = self.sess.get(url=url, headers=self.headers, params=params).json()
        if 'retcode' in response and response['retcode'] == 0 and 'pubkey' in response:
            logging.info('公钥获取成功。')
            return response
        else:
            logging.error('公钥获取失败，请检查网络。')
            sys.exit()

    def get_sp(self, pubkey_json):
        """
        # description: 通过公钥等数据加密密码
        # param json pubkey_json 获取的公钥字典
        # return str sp 256位加密私钥
        """

        pubkey = pubkey_json['pubkey']
        servertime = pubkey_json['servertime']
        nonce = pubkey_json['nonce']
        public_key = rsa.PublicKey(int(pubkey, 16), int('10001', 16))
        password_str = str(servertime) + '\t' + str(nonce) + '\n' + self.password
        sp = b2a_hex(rsa.encrypt(password_str.encode('utf8'), public_key)).decode('utf8')
        return sp

    def figure_code(self, pcid, report=None):
        """
        # description: 使用快识平台识别验证码
        # param str pcid pubkey中标识设备的字段，用于请求验证码
        # param str report 识别失败后向验证码识别平台提交错误
        # return (str,str) (id,result) 图片ID与识别结果
        # 请求链接：https://login.sina.com.cn/cgi/pin.php
        """

        code_url = f'https://login.sina.com.cn/cgi/pin.php?r={str(random())[:-9:-1]}&s=0&p={pcid}'
        ocr_url = f'http://api.95man.com:8888/api/Http/Recog?Taken={self.ocr_token}&imgtype=1&len=5'
        if report:
            report_url = f'http://api.95man.com:8888/api/Http/ReportErr?Taken={self.ocr_token}&ImgID={report}'
            requests.get(report_url)
        pic = self.sess.get(code_url).content
        r = requests.post(ocr_url, files={'imgfile': ('code.png', pic)}).text
        arrstr = r.split('|')
        if int(arrstr[0]) > 0:
            logging.info(f'验证码识别结果：{arrstr[1]}')
            return arrstr[0], arrstr[1]
        else:
            logging.warning('识别出错，返回：hello')
            return 'hello'

    def pre_login(self, pubkey_json, codes=None):
        """
        # description: 微博预登录，返回微博登录ticket以及跨域链接
        # param dict pubkey_json 公钥数据
        # param str codes 可能需要验证码
        # return dict response 用户数据以及跨域链接等
        # 请求链接：https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)
        # 一个返回示例：
        {
            'retcode': '0',
            'uid': '6015545982',
            'nick': 'gugubot',
            'crossDomainUrlList': [
                'https://passport.weibo.com/wbsso/login?ticket=ST-NjAxg%3D%3D-1607088902-yf-9565C190264-1&ssosavestate=1638624902',
                'https://passport.97973.com/sso/crossdomain?action=login&savestate=1638624902',
            ]
        }
        """

        url = f'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)&_={round(time() * 1000)}'
        data = {
            'entry': 'cnmail',
            'gateway': '1',
            'from': '',
            'savestate': '30',
            'qrcode_flag': 'false',
            'useticket': '0',
            'pagerefer': '',
            'service': 'sso',
            'pwencode': 'rsa2',
            'sr': '1356*864',
            'encoding': 'UTF-8',
            'prelt': '95',
            'cdult': '3',
            'domain': 'sina.com.cn',
            'returntype': 'TEXT',
            'servertime': pubkey_json['servertime'],
            'nonce': pubkey_json['nonce'],
            'rsakv': pubkey_json['rsakv'],
            'pcid': pubkey_json['pcid'],
            'su': self.su,
            'sp': self.get_sp(pubkey_json),
        }
        if codes:
            data['door'] = codes[1]
        response = self.sess.post(url=url, headers=self.headers, data=data).json()
        if 'retcode' in response:
            if response['retcode'] == '0' and 'crossDomainUrlList' in response:
                logging.info('预登录成功。')
                return response
            elif response['retcode'] == '101':
                logging.error('用户名或密码错误。')
                sys.exit()
            elif response['retcode'] == '4049':
                logging.info('需要输入验证码。')
                return self.pre_login(pubkey_json, codes=self.figure_code(pubkey_json['pcid']))
            elif response['retcode'] == '2070':
                logging.warning('识别错误，继续尝试中。')
                return self.pre_login(pubkey_json, codes=self.figure_code(pubkey_json['pcid'], codes[0]))
            elif response['retcode'] == '2071':
                logging.warning('需要扫码登录！')
            else:
                logging.error(response['reason'])
                sys.exit()
        else:
            logging.error('预登录失败，请检查网络。')
            sys.exit()

    def cross_login(self, pre_json):
        """
        # description: 使用跨域链接登录微博
        # param dict pre_json 预登录得到的json，包括跨域链接
        # return dict response 登录结果与用户数据
        # 一个返回示例：{'result': True, 'userinfo': {'uniqueid': '6015545982', 'displayname': '鸽鸽bot'}}
        """

        url = pre_json['crossDomainUrlList'][0]
        response = self.sess.get(url=url, headers=self.headers).text
        response = loads(response[1:-3])
        if 'result' in response and response['result']:
            logging.info('微博登录完成。')
            return response
        else:
            logging.error('登录失败，请检查网络。')

    def cookies_login(self):
        cookies_name = 'COOKIES-' + self.su[:8]
        if cookies_name in listdir():
            with open(cookies_name, 'rb') as f:
                self.sess = pickle.load(f)
            try:
                response = self.sess.get("https://weibo.com/ajax/side/cards/sideInterested?count=-1").json()
                if "ok" in response and response["ok"] == 1:
                    logging.info('从文件中恢复Cookie成功，跳过登录。')
                    return True
            except json.decoder.JSONDecodeError:
                logging.warning('Cookie失效，使用账号密码登录。')
        else:
            logging.info('初次登录未发现Cookie，使用账号密码登录。')
        return False

    def sess_update(self):
        response = self.sess.get("https://weibo.com")
        self.sess.headers.update({
            'origin': 'https://weibo.com',
            'referer': 'https://weibo.com',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69',
            'x-xsrf-token': requests.utils.dict_from_cookiejar(self.sess.cookies)["XSRF-TOKEN"]
        })
        response = self.sess.get("https://rm.api.weibo.com/2/remind/push_count.json")

    def main(self):
        """
        # description: 登录主函数，按流程完成登录操作
        """

        try:
            if self.cookies_flag and self.cookies_login():
                logging.info('成功使用cookies登录')
            else:
                pubkey_json = self.get_pubkey()
                pre_json = self.pre_login(pubkey_json)
                self.cross_login(pre_json)
            self.sess_update()
            cookies_name = 'COOKIES-' + self.su[:8]
            with open(cookies_name, 'wb') as f:
                pickle.dump(self.sess, f)
                logging.info('新的Cookie已保存。')

        except Exception:
            logging.error('失败，发生了一个错误！', exc_info=True)
            sys.exit()


if __name__ == '__main__':
    login = Login()
    login.main()
    logging.info("#-#-#-#-#-#-#-#-#-#-#-#-#")
