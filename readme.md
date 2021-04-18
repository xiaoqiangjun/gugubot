# gugubot -- 微博咕咕机器人  


项目基于`python3.6+`与`requests`模块，纯手工模拟微博登录、发布微博、上传图片、发布定时微博等功能。  

**项目最佳实践**：[鸽鸽bot](https://weibo.com/u/6015545982)  （欢迎关注）

## 如何运行
 - 克隆仓库，并确保有`python3.6+`环境与`requests`模块
 - 一个微博账号，并使用该账号注册了[新浪邮箱](https://mail.sian.com.cn)**（重要）**
 - 在`weibo.py`或`gugubot.py`文件末尾添加账号信息
 - 配置`log.json`中`error_mail_handler`字段或直接删除此字段
 - 齐活

## 文件介绍
 - `login.py` - 模拟微博登录流程，获取微博cookies
 - `weibo.py` - 实现发布微博功能，包括单文本微博、图片微博、定时微博等
 - `gugubot.py` - 基于上述模块，实现了整点发布报时微博的功能，并且实现了自动转发每日必应图片、今日诗词等功能

## License
GPL v3.0