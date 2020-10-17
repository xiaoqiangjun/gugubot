import requests
import re
import os
from calendar import timegm
from time import *


def wait_on_time():
    '''硬延时到整点'''
    wkt_list = list(gmtime(time()))
    if wkt_list[3] == 23:
        wkt_list = list(gmtime(time() + 86400))
        wkt_list[3] = 0
    else:
        wkt_list[3] += 1
    wkt_list[4] = 0
    wkt_list[5] = 0

    work_time = timegm(tuple(wkt_list))
    print(strftime('work at: UTC %Y-%m-%d %H:%M:%S', tuple(wkt_list)))
    now_time = time()
    print(strftime('now its: UTC %Y-%m-%d %H:%M:%S', gmtime(time())))
    remain_time = work_time - now_time
    if remain_time < 0 or remain_time > 1800:
        print('OUT OF WORK TIME!')
        return None
    while remain_time > 0:
        if remain_time > 100:
            print('time remians:', '{:0>2d}'.format(round(remain_time)), 's')
            print('long time sleep...')
            sleep(77)
            remain_time = work_time - time()
            continue
        print('time remians:',
              '{:0>2d}'.format(round(remain_time)),
              's',
              end='')
        sleep(1)
        print("\r", end='', flush=True)
        remain_time = work_time - time()

    print('*-*-*-*-*-*-*-**-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*')
    print(
        strftime('WORK STARTING SUCCESSFULLY AT UTC %Y-%m-%d %H:%M:%S',
                 gmtime(time())))
    print('*-*-*-*-*-*-*-**-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*')


def time_bar(now_hour):
    '''输出咕咕bot问候与时间进度条'''
    str1 = '我是您的🕊🕊机器人，现在是北京时间%d点整，%s~~~\n' % (now_hour, '咕' * now_hour if now_hour!=0 else '没得咕')
    str2 = '今日进度条: %s%s\n' % ('◼' * (now_hour), '◻' * (24 - now_hour))
    return str1 + str2


def get_shici():
    '''获取诗词，使用随机接口'''
    url = 'https://v1.jinrishici.com/all.json'
    response = requests.get(url).json()
    dicts = {}
    if response:
        dicts['content'] = response['content']
        dicts['title'] = response['origin']
        dicts['author'] = response['author']
    return dicts


def get_weather():
    '''获取天气，数据来自彩云天气'''
    city = '武汉'
    coordinates = '114.4169,30.5095'
    caiyun_token = os.environ['CAIYUN_TOKEN']
    url = f'https://api.caiyunapp.com/v2.5/{caiyun_token}/{coordinates}/weather.json?hourlysteps=5&dailysteps=3'
    CODE = {'CLEAR_DAY': '晴', 'CLEAR_NIGHT': '晴夜', 'PARTLY_CLOUDY_DAY': '多云', 'PARTLY_CLOUDY_NIGHT': '云夜', 'CLOUDY': '阴', 'LIGHT_HAZE': '轻度雾霾', 'MODERATE_HAZE': '中度雾霾','HEAVY_HAZE': '重度雾霾', 'LIGHT_RAIN': '小雨', 'MODERATE_RAIN': '中雨', 'HEAVY_RAIN': '大雨', 'STORM_RAIN': '暴雨', 'FOG': '雾', 'LIGHT_SNOW': '小雪', 'MODERATE_SNOW': '中雪', 'HEAVY_SNOW': '大雪', 'STORM_SNOW': '暴雪', 'DUST': '浮尘', 'SAND': '沙尘', 'WIND': '大风'}
    req = requests.get(url).json()
    dicts = {}
    realtime = req['result']['realtime']
    hourly = req['result']['hourly']
    daily = req['result']['daily']
    dicts['realtime'] = CODE[realtime['skycon']]
    dicts['temperature'] = round(realtime['temperature'])
    dicts['api'] = realtime['air_quality']['description']['chn']
    dicts['description'] = req['result']['minutely']['description']
    dicts['next_5h'],temp = [],{}
    for index in range(5):
        temp['datetime'] = hourly['skycon'][index]['datetime'][11:16]
        temp['temperature'] = round(hourly['temperature'][index]['value'])
        temp['skycon'] = CODE[hourly['skycon'][index]['value']]
        dicts['next_5h'].append(temp.copy())
    dicts['next_2d'] = []
    for index in [1,2]:
        v1 = daily['skycon'][index]['value']
        v2 = daily['skycon_08h_20h'][index]['value']
        if v1 == v2:
            dicts['next_2d'].append(CODE[v1])
        else:
            dicts['next_2d'].append(CODE[v1] + '转' + CODE[v2])
    dicts['astro'] = [daily['astro'][0]['sunrise']['time'],daily['astro'][0]['sunset']['time']]
    return dicts


def format_weather(dicts,now_hour):
    '''返回天气字符串'''
    string = '\n来看看天气吧！\n'
    string += f"武汉现在{dicts['realtime']}，气温{dicts['temperature']}℃，空气质量{dicts['api']}。\n"
    # string += f"武汉现在{dicts['realtime']}，气温{dicts['temperature']}℃，空气质量{dicts['api']}。{dicts['description']}。\n"
    # string += '未来3小时天气预报：\n'
    # for index in range(5):
    #     temp = dicts['next_5h'][index]
    #     string += f"{temp['datetime']}：{temp['skycon']}，气温{temp['temperature']}℃；\n"
    if now_hour == 7:
        string += f"\n🌄: {dicts['astro'][0]}   🌆: {dicts['astro'][1]}"
    elif now_hour == 21:
        string += f"\n未来两天天气预报，明天{dicts['next_2d'][0]}，后天{dicts['next_2d'][1]}。"
    else:
        string += '\n注意天气，好好午睡哦。'
    return string


def get_dailyeng_sb():
    '''每日英语，来自扇贝'''
    url = 'https://rest.shanbay.com/api/v2/quote/quotes/today/'
    response = requests.get(url).json()
    dicts = {}
    if response['msg'] == 'SUCCESS':
        dicts['content_sb'] = response['data']['content']
        dicts['translation'] = response['data']['translation']
    return dicts


def get_dailyeng_ol():
    '''每日英语，来自欧陆'''
    url = 'http://dict.eudic.net/home/dailysentence'
    response = requests.get(url).text
    dicts = {}
    dicts['content_ol'] = re.search(r'sect_en">(.*?)</p>', response).group(1)
    dicts['translation'] = re.search(r'-trans">(.*?)<', response).group(1)
    return dicts


def get_dailyeng_cb():
    '''每日英语，来自词霸'''
    url = 'http://open.iciba.com/dsapi/'
    response = requests.get(url).json()
    dicts = {}
    if response:
        dicts['content_cb'] = response['content']
        dicts['translation'] = response['note']
    return dicts


def get_bing():
    '''获取bing每日图片'''
    url = 'https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=zh-CN'
    response = requests.get(url).json()['images'][0]
    dicts = {}
    dicts['date'] = response['enddate']
    dicts['id'] = re.search(r'=(.*?)_1', response['url']).group(1)
    dicts[
        'url'] = 'https://cn.bing.com/th?id=' + dicts['id'] + '_UHD.jpg'
    dicts['copyright'] = response['copyright']
    return dicts


def get_attachment(now_hour): 
    '''附加微博内容'''
    dicts = {}
    if now_hour in [2,4,9,11,13,15,17,19,22,23]:
        dicts = get_shici()
        string = (f"\n来读诗吧：\n{dicts['content']}\n‏{dicts['author']}《{dicts['title']}》")
    elif now_hour in [7,12,21]:
        dicts = get_weather()
        string = format_weather(dicts,now_hour)
    elif now_hour in [6,10,14]:
        if now_hour == 6:
            dicts = get_dailyeng_ol()
            string = (f"\n今日英语，来自欧陆。\n{dicts['content_ol']}\n{dicts['translation']}")
        elif now_hour == 10:
            dicts = get_dailyeng_sb()
            string = (f"\n今日英语，来自扇贝。\n{dicts['content_sb']}\n{dicts['translation']}")
        else:
            dicts = get_dailyeng_cb()
            string = (f"\n今日英语，来自词霸。\n{dicts['content_cb']}\n{dicts['translation']}")
    elif now_hour == 8:
        dicts = get_bing()
        string = (f"\n今日必应图片：{dicts['copyright']}\n图片高清地址 {dicts['url']}")
    else:
        string = '\n难得无事的咕咕bot，看张图片，休息一会吧。'
    string += ('\nhttp://t.cn/A6bpoKJC')
    return dicts,string


def post_weibo(string,dicts,now_hour):
    '''发布微博'''
    weibo_url = "https://api.weibo.com/2/statuses/share.json"
    if now_hour in [0, 1, 3, 5, 16, 18, 20]:
        pic_url = 'https://source.unsplash.com/featured/1080x1920?nature,mountain'
    elif now_hour == 8:
        pic_url = dicts['url'].replace('UHD','1920x1080')
    else:
        pic_url = 'https://source.unsplash.com/featured/1080x1920?nature,mountain'
    payload = {
        "access_token": os.environ['WEIBO_TOKEN'],
        "status": string
    }
    print(string)
    if pic_url:
        files = requests.get(pic_url).content
        r = requests.post(weibo_url, data=payload, files={'pic': files})
    else:
        r = requests.post(weibo_url, data=payload)
    return r.json()


def save_log(dicts,now_hour):
    '''保存各种日志'''
    if 'title' in dicts:
        data = dicts['content'] + ',' + dicts['title'] + ',' + dicts['author'] + '\n'
        with open('shici_log.csv', 'a+', encoding='utf8') as log_file:
            log_file.write(data)   
    elif 'realtime' in dicts:
        data = str(now_hour) + ',' + dicts['realtime'] + ',' + dicts['temperature'] + ',' + dicts['api']
        data += ',' + dicts['description'] + ',' + dicts['next_2d'][0] + ',' + dicts['next_2d'][1]
        data += ',' + dicts['astro'][0] + ',' + dicts['astro'][1]
        with open('weather_log.csv', 'a+', encoding='utf8') as log_file:
            log_file.write(data)
    elif 'id' in dicts:
        data = dicts['date'] + ',' + dicts['id'] + ',' + dicts['url'] + ',' + dicts['copyright'] + '\n'
        with open('bing_log.csv', 'a+', encoding='utf8') as log_file:
            log_file.write(data)
    elif 'content_cb' in dicts:
        data = dicts['content_cb'] + ',' + dicts['translation'] + '\n'
        with open('cb_log.csv', 'a+', encoding='utf8') as log_file:
            log_file.write(data)
    elif 'content_ol' in dicts:
        data = dicts['content_ol'] + ',' + dicts['translation'] + '\n'
        with open('ol_log.csv', 'a+', encoding='utf8') as log_file:
            log_file.write(data)
    elif 'content_sb' in dicts:
        data = dicts['content_sb'] + ',' + dicts['translation'] + '\n'
        with open('sb_log.csv', 'a+', encoding='utf8') as log_file:
            log_file.write(data)
    else:
        with open('log.csv', 'a+', encoding='utf8') as log_file:
            log_file.write('咕\n')


if __name__ == "__main__":
    # 提前启动，等待整点
    #wait_on_time()
    
    # 现在时间（北京）
    now_hour = gmtime(time()+28800)[3]
    
    # 整点问候与时间进度条
    # string = time_bar(now_hour)
  
    # 附加内容
    # dicts, attachment = get_attachment(now_hour)
    
    string = '%s\n' % (('咕' * now_hour + '~~~') if now_hour!=0 else '没得咕...')
    attachment = '\nhttp://t.cn/A6bpoKJC'
    dicts = {}
    if now_hour == 8:
        dicts, attachment = get_attachment(now_hour)
        save_log(dicts,now_hour)
    
    # 发布微博
    response = post_weibo(string+attachment, dicts, now_hour)

    # 结果保存与输出
    if 'created_at' in response:
        # save_log(dicts,now_hour)  
        print('Success! Created at: ' + str(response['created_at']))
    else:
        print(response)

    # 字符超出限制
    # 字符串转码不完整