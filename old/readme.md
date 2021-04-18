gugubot --微博咕咕机器人
===
项目基于`python3.x`与`requests`模块，利用`Github Actions`实现整点准时播报，并自动发布微博，目前已实现以下功能： 

- 整点播报
    - 24小时整点播报
    - 咕咕对应声
    - 当日时间进度条
- 随机一句诗词
    - 在`2,4,9,11,13,15,17,19,22,23`整点播报
    - 使用[今日诗词](https://www.jinrishici.com/)提供的随机诗词[API](https://v1.jinrishici.com/all.json)
- 天气预报
    - 在`7,12,21`整点播报
    - 实时天气、气温与aqi指数
    - 未来五小时天气预报（改为3小时仍会超出140字符限制，在没有找到解决方法前删除这部分内容）
    - 在`7`点播报日出日落时间
    - 在`21`点预报明后天天气
    - 使用[彩云天气](http://www.caiyunapp.com/)API
- 每日英语
    - 在`6,10,14`整点播报
    - 分别使用[欧陆词典](http://dict.eudic.net/home/dailysentence)、[扇贝单词](https://rest.shanbay.com/api/v2/quote/quotes/today/)和[金山词霸](http://open.iciba.com/dsapi/)API或网页数据
- 每日必应图片
    - 在`8`点播报
    - 原来[bing2weibo仓库](https://github.com/xiaoqiangjun/bing2weibo)停止使用
- 随机图片
    - 在其余的整点时间添加随机图片
    - 使用[unsplash](https://source.unsplash.com/)随机图片API
- 备份日志
    - 使用`Github Actions`自动备份数据到仓库
    - 包括诗词、每日英语与必应图片数据

## license
GPL v3.0