## 介绍

CSUST一群无聊的人开发，在Telegram上使用。
在Telegram搜索 [@csust_bot](https://telegram.me/csust_bot) 即可找到该bot。
欢迎加入 [CSUST Telegram 技（xian）术（liao）群](https://t.me/csuster) 。

## 开发&&使用

只在Python3环境开发测试，不保证Python2能够运行。
需要安装的库有：

1. ` python-telegram-bot` 使用pip安装即可
2. `requests` 用于同图灵机器人发起交流。
3. `googletrans` 咕果翻译

## 快速部署

使用root用户执行以下命令（目前只支持Linux发行版）：

```bash
bash <(curl -sL https://raw.githubusercontent.com/CSUSTers/csust_bot/master/letsgo.sh)
```

## 使用docker部署

1. 安装docker
2. 切换到项目所在目录
3. 执行 `docker build ./`
4. 记下构建的docker镜像 `id` => `{{id}}`
5. 执行 `docker run --name {{name you want}} -d {{id}}`
