"""
# Author: Xiaoqiangjun
# Date: 2021-04-18 20:51:10
# LastEditTime: 2021-05-27 11:25:18
# LastEditors: Please set LastEditors
# FilePath: /gugubot/gugubot.py
"""
from datetime import datetime, timedelta
import re
import requests
import weibo
import logging

def get_bing():
    """获取bing每日图片"""
    url = 'https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=zh-CN'
    response = requests.get(url).json()['images'][0]
    dicts = {}
    if response:
        dicts = {
            'date': response['enddate'],
            'id': re.search(r'=(.*?)_1', response['url']).group(1),
            'copyright': response['copyright']
        }
        dicts['url'] = 'https://cn.bing.com/th?id=' + dicts['id'] + '_UHD.jpg'
    return dicts

def get_shici():
    """获取一句随机诗词"""
    url = 'https://v1.jinrishici.com/all.json'
    response = requests.get(url).json()
    dicts = {}
    if response:
        print(response)
        dicts['content'] = response['content']
        dicts['title'] = response['origin']
        dicts['author'] = response['author']
    return dicts

def make_weibo_string(hour):
    """设置某个时间的微博内容"""
    gugu = '%s' % (('咕' * hour) if hour != 0 else '喵')
    if hour == 8:
        bing = get_bing()
        string = f"{gugu}\n\n今日必应图片：{bing['copyright']}\n图片高清地址 {bing['url']}"
        return {'string': string, 'bing': bing['url']}
    elif hour == 13:
        shici = get_shici()
        string = f"{gugu}\n\n每日诗词：\n{shici['content']}\n‏{shici['author']}《{shici['title']}》"
        return {'string': string, 'shici': 'shici'}
    else:
        return {'string': gugu, 'normal': 'gugugu'}

def post_weibo(wb, missed_time):
    """按规则使用不同的函数发布"""
    for mt in missed_time:
        weibo_dict = make_weibo_string(mt[0])
        if 'bing' in weibo_dict:
            wb.post_weibo(weibo_dict['string'], intime=mt[1], pic=wb.get_picid([weibo_dict["bing"]]))
        elif 'shici' in weibo_dict:
            wb.post_weibo(weibo_dict['string'], intime=mt[1])
        elif 'normal' in weibo_dict:
            wb.post_weibo(weibo_dict['string'], intime=mt[1])

def check_time(lists, length):
    """检查下几个整点微博是否已定时"""
    missed_time = []
    now_list = set([x[1] for x in lists])
    now0 = datetime.now().replace(minute=0, second=0, microsecond=0)
    for i in range(length):
        now0 += timedelta(hours=1)
        tmp = int(now0.timestamp())*1000
        if tmp not in now_list:
            missed_time.append((now0.hour,tmp))
    logging.info("现在有%d条定时微博，需要新发布%d条" % (len(now_list),len(missed_time)))
    return missed_time


if __name__ == "__main__":
    # 初始化
    username = ""   # 你的微博账号
    password = ""   # 你的微博密码
    ocr_token = ""  # orc密钥，如果需要填写图片字母数字的验证码，可以在fast.95man.com申请，否则可以留空
    cookies_flag = True # 是否保留Cookies,下次无需再次登录，建议开启

    comfirm_weibo_length = 5 # 检查后几个整点

    # 微博登录
    # wb = weibo.Weibo(os.environ['username'],os.environ['password'],os.environ['token'])
    wb = weibo.Weibo(username, password, ocr_token, cookies_flag)
    wb.weibo_login()

    # 定时列表
    lists = wb.get_intime_weibo()

    # 检查下几个整点微博
    missed_time = check_time(lists, comfirm_weibo_length)

    # 发布微博
    post_weibo(wb, missed_time)