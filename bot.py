#!/usr/bin/env python3
"""
commands:
say_hello - 我是一只只会嗦hello的咸鱼
hello_to_all - Say hello to all group members
record - 人类的本质就是复读机，Bot也是一样的

----------
"""

from telegram.ext import Updater, CommandHandler
from telegram import error, bot

import json


def load_json():
    with open("data.json", "r") as file:
        return json.load(file)


def fiddler(cmdstr):
    l = cmdstr.split(' ')
    if '/' in l[0]:
        return ' '.join(l[1:])
    else:
        return cmdstr


def start(bot, update):
    update.message.replyText('This is a bot made by some csusters stadying SE,\n' 
                             ' and serve every csusters.',
                             parse_mode='Markdown')


def say_hello(bot, update):
    chatId = update.message.chat_id
    replyText = "Hello.\n"
    try:
        update.message.reply_text(replyText,
                                  parse_mode='Markdown')
    except error.NetworkError:
        update.message.reply_text(replyText)


def hello_to_all(bot, update):
    chatId = update.message.chat_id
    replyText = '大家好，我是一只只会嗦hello的咸鱼.\n'
    update.message.reply_text(replyText)


def record(bot, update):
    replyText = fiddler(update.message.text)
    update.message.reply_text(replyText)


def main():
    updater = Updater(token='TOKEN')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('say_hello', say_hello))
    dp.add_handler(CommandHandler('hello_to_all', hello_to_all))
    dp.add_handler(CommandHandler('record', record))
    updater.start_polling()


if __name__ == '__main__':
    main()

