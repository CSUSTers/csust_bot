#!/usr/bin/env python3

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler
from telegram import error, bot

import requests
import json
import re


def weather_qy(bot, update, args):
    # cty = ''.join(args)
    # city = ''
    # for c in cty:
    #    if '\u4e00' <= c <= '\u9fff':
    #        city += c

    city = ''.join(re.split(r'[!@#$%^&*\(\):"<>?;,./*-+=]', ' '.join(args)))
    if len(city) == 0:
        bot.send_message(update.message.chat_id, '您想查询什么城市呢~')
    else:
        url = 'http://api.map.baidu.com/telematics/v3/weather?location=%s&output=json&ak=TueGDhCvwI6fOrQnLM0qmXxY9N0OkOiQ' \
              '&callback=?' % city
        replyText = ''
        rs = requests.get(url)
        rs_dict = json.loads(rs.text)
        error_code = rs_dict['error']
        if error_code == 0:
            results = rs_dict['results']
            info_dict = results[0]
            city_name = info_dict['currentCity']
            replyText = city_name + '最近的天气请查收~~\n'
            weather_data = info_dict['weather_data']
            for weather_dict in weather_data:
                date = weather_dict['date']
                weather = weather_dict['weather']
                wind = weather_dict['wind']
                temperature = weather_dict['temperature']
                replyText = replyText + date + ': ' + weather + ' ' + wind + temperature + '\n'
        else:
            replyText = '没有查询到'+city+'的天气信息哦~~'
        bot.send_message(update.message.chat_id, replyText)
