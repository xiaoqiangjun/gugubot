"""
# Author: Xiaoqiangjun
# Date: 2021-04-14 22:07:19
# LastEditTime: 2021-04-18 21:59:06
# LastEditors: Xiaoqiangjun
# FilePath: /gugubot/weibo.py
"""

import logging
from base64 import b64encode
from datetime import datetime, timedelta
from time import sleep

import requests

import login


class Weibo:
    """
    封装微博登录与文字图片微博发布，全面使用新版网页微博(除了图片上传)
    """
    def __init__(self, username, password, token=None, cookies_flag=True, post_delay=5):
        """
         # description: 使用用户名，密码，ocr密钥等初始化Login类
         # param int/str username 用户名、邮箱、手机号等
         # param str password 密码
         # param bool cookies_flag 是否尝试使用以保存的cookies登录
         # param str token 快识平台 fast.95man.com 验证码识别令牌
         # return None
        """
        self.post_delay = post_delay
        self.loginweibo = login.Login(username, password, token, cookies_flag)

    def weibo_login(self):
        """
        # description: 登录操作
        # param None
        # return None
        """

        self.loginweibo.main()
        self.sess = self.loginweibo.sess

    def post_weibo(self, text, intime=None, pic=None, rank=0):
        """
        # description: 发送微博的基础函数
        # param str text 微博文字内容
        # param str intime 定时微博发布时间的时间戳（毫秒）
        # param str pic 微博图片id，以逗号分隔
        # param int rank 可以查看微博的人 1仅自己 0公开 6好友圈 10粉丝
        # return dict response 微博返回数据
        """

        url = "https://weibo.com/ajax/statuses/update"
        if intime: url = "https://weibo.com/ajax/statuses/schedule/upload"
        data = {"share_id": "", "media": "{}", "vote": "{}", "pic_id": "", "visible": rank, "content": text}
        if pic: data["pic_id"] += pic
        if intime: data["schedule_timestamp"] = intime
        response = self.sess.post(url=url, data=data).json()
        if "ok" in response and response["ok"] == 1:
            if intime:
                logging.info('定时微博设置成功，时间为: %s' % str(datetime.fromtimestamp(int(intime)//1000)))
            else:
                logging.info("微博发布成功。")
            logging.info("内容为：%s" % text)
            sleep(self.post_delay)
        return response

    def get_intime(self, intime):
        """
        # description: 转换定时微博的时间
        # param str intime 定时微博发布时间，支持以下格式：
            1. 毫秒时间戳，例如：1618588800000
            2. "+n"字符串，表示当前时间后面的第n个整点，例如现在19:45，"+2"表示21:00
            3. 标准格式时间字符串，形式为：2021-04-17 08:00:00
        # return int timestmp 转换后时间戳
        """

        if intime.isdigit():
            timestamp = int(intime)
        elif intime[0] == "+":
            n = int(intime[1:])
            now0 = datetime.now().replace(minute=0, second=0, microsecond=0)
            now0 += timedelta(hours=n)
            timestamp = int(now0.timestamp() * 1000)
        else:
            temp = datetime.fromisoformat(intime)
            timestamp = int(temp.timestamp() * 1000)
        return timestamp

    def get_picid(self, paths):
        """
        # description: 上传图片，获取id
        # param list.str paths 待发送图片地址，支持网络图片（包括http头的）与本地图片
            例如：["https://www.baidu.com/bd.png","F:/desktop/b107.png"]
        # return str 图片id字符串
        """
        pid = []
        for path in paths:
            p = None
            if "http" in path.lower():
                try:
                    file = requests.get(path).content
                    p = self.upload_pic(file)
                except requests.RequestException:
                    pass
            else:
                try:
                    with open(path, 'rb') as f:
                        p = self.upload_pic(f.read())
                except IOError:
                    pass
            if p: pid.append(p)
        logging.info("共有%d张图片，成功上传%d张图片" % (len(paths),len(pid)))
        if pid:
            return ",".join(pid)

    def upload_pic(self, file):
        """
        # description: 上传图片到微博，非新版微博使用接口
        # param bytes-like file 待上传图片数据
        # return str pid 微博图片id
        """

        url = 'https://picupload.weibo.com/interface/pic_upload.php?data=base64'
        data = {'b64_data': b64encode(file)}
        response = self.sess.post(url=url, data=data).text
        if 'A00006' in response:
            pid = response[-37:-5]
            logging.info('图片上传成功。pid:%s' % pid)
            return pid
        else:
            logging.warning('图片上传失败。')
        sleep(self.post_delay)

    def get_intime_weibo(self):
        """
        # description: 获取已发布定时微博数据
        # param None
        # return list.list weibo_list 定时微博列表，格式为[tid, tm, text]
            例如：[['4627425050499719', '1618834560', 'asfa'],
                  ['4627425097420565', '1618920960', '242g']]
        """

        url = "https://weibo.com/ajax/statuses/schedule/list?type=0&max_id="
        response = self.sess.get(url).json()
        weibo_list = []
        if "ok" in response and response["ok"] == 1:
            lists = response["data"]["statuses"]
            for item in lists:
                text = item["text"]
                tid = item["schedule_id"]
                tm = int(datetime.strptime(item["schedule_at"],"%a %b %d %X %z %Y").timestamp())*1000
                weibo_list.append([tid, tm , text])
            weibo_list.sort(key=lambda x: x[2])
        return weibo_list


if __name__ == '__main__':
    weibo = Weibo()
    weibo.weibo_login()
    pic = weibo.get_picid(["https://www.runoob.com/wp-content/uploads/2014/05/python3.png"])
    tm = weibo.get_intime("+3")
    weibo.post_weibo("test23",intime=tm,rank=1)


