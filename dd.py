import re
import requests
from random import randint


def get_shici():
    '''诗词'''
    url = 'https://v2.jinrishici.com/sentence'
    header = {'X-User-Token': 'jgFnzwQiuDEL0ZjTXyiTVwxbaaUnkWSA'}
    response = requests.get(url, headers=header).json()
    dicts = {}
    if response['status'] == 'success':
        dicts['content'] = response['data']['content']
        dicts['title'] = response['data']['origin']['title']
        dicts['author'] = response['data']['origin']['author']
    return dicts


def get_dailyeng_sb():
    '''每日英语，来自扇贝'''
    url = 'https://rest.shanbay.com/api/v2/quote/quotes/today/'
    response = requests.get(url).json()
    dicts = {}
    if response['msg'] == 'SUCCESS':
        dicts['content'] = response['data']['content']
        dicts['translation'] = response['data']['translation']
    return dicts


def get_dailyeng_ol():
    '''每日英语，来自欧陆'''
    url = 'http://dict.eudic.net/home/dailysentence'
    response = requests.get(url).text
    dicts = {}
    dicts['content'] = re.search(r'sect_en">(.*?)</p>', response).group(1)
    dicts['translation'] = re.search(r'-trans">(.*?)<', response).group(1)
    return dicts


def get_random_name(length=8):
    '''返回给定长度的随机字符串'''
    str = ''
    STRLIST = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    for _ in range(length):
        str += STRLIST[randint(0, len(STRLIST) - 1)]
    return str


def get_menhera():
    '''获取随机表情包'''
    url = 'https://acg.yanwz.cn/menhera/api.php'
    header = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36 Edg/86.0.622.38'
    }
    name = 'menhera_' + get_random_name() + '.png'
    response = requests.get(url, headers=header).content
    with open(name, 'wb') as fo:
        fo.write(response)


def get_cat():
    '''随机获取一张猫猫图'''
    url = 'https://api.thecatapi.com/v1/images/search'
    header = {'x-api-key': 'af6447e9-32da-4b82-b7bd-7da759d1aa90'}
    pic_url = requests.get(url, headers=header).json()[0]['url']
    response = requests.get(pic_url).content
    name = 'cat_' + get_random_name() + pic_url[-4:]
    with open(name, 'wb') as fo:
        fo.write(response)


def main():
    # 一句古诗词
    shici = get_shici()
    print(shici)

    # 每日英语--扇贝
    dailyeng = get_dailyeng_sb()
    print(dailyeng)

    # 每日英语--欧陆
    dailyeng = get_dailyeng_ol()
    print(dailyeng)

    # menhera酱表情包
    get_menhera()
    get_menhera()

    # 随机猫猫图
    get_cat()


if __name__ == "__main__":
    print('hello world')
    main()