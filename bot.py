#!/usr/bin/env python3

"""
commands:
say_hello - 我是一只只会嗦hello的咸鱼
hello_to_all - Say hello to all group members
record - 人类的本质就是复读机，Bot也是一样的
real_record - 复读机...复读机...复读机的开关
all_links - 这里有一些链接，如果本校同学想要添加友链也可以联系哦
all_questions - 显示所有的问题
all_answers - 显示所有的问题和答案
answer - <Num>  回答指定的问题
question - 随机问题
google - <Key Words> Search Google...
ddg - <Key Words> Search DuckDuckGo...
bing - <Key Words> Search Bing...
search_baidu - <Key Words> 在百毒搜索...
weather - <CityName> 查询天气
banmyself - 把自己ban掉[36,66]秒
fake_banmyself - 虚假的ban自己
chat - [message] 与机器人聊天，有参数时将回复参数，无参数时做为自动聊天的开关

----------
"""
import datetime

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler
from telegram import error, Bot, Chat, User, Message, ChatMember, Sticker

from config import TOKEN
from weather_query import weather_qy
from utils import SecGetter
from turing_robot import turing_robot

import json
import random
import logging
import utils
import requests
import sys, os


# for new feature
data_dict = {}
QnA_dict = {}
links_dict = {}
about_str = ''
question_keys = []
main_links = []
friend_links = []
questions = {}
answers = {}

# for real_record
chat_id_list = []

# for turing_chat
turing = turing_robot()
turing_chat_list = []

# working path
# working_path = ''

def load_json():
    # global working_path
    # with open(os.path.join(working_path, "data.json"), "r") as file:
    #     return json.load(file)
    with open('data.json', 'r') as file:
        return json.load(file)


def fiddler(cmdstr):
    l = cmdstr.split(' ', 1)
    if l[0].startswith('/'):
        return l[1]
    else:
        return cmdstr


def start(bot, update):
    update.message.reply_text('This is a bot made by some csusters stadying SE,\n'
                              ' and serve every csusters.',
                              parse_mode='Markdown')


def banmyself(bot, update):
    cmd_list = update.message.text.split()[1:]
    long_long_time = 0
    if len(cmd_list) > 0:
        long_long_time = SecGetter.get(cmd_list)
    
    
    chatid = update.message.chat_id
    user_id = update.message.from_user.id
    if update.message.chat.type == 'private':
        update.message.reply_text('我觉得布星~')
    elif bot.get_chat_member(chatid, bot.id).status == 'administrator':
        if bot.get_chat_member(chatid, user_id).status in ['administrator','creator']:
            update.message.reply_text('神秘的力量使我无法满足你的欲望')
        else:
            if 36 < long_long_time < 262400:
                ban_sec = long_long_time
            else:
                ban_sec = random.choice(range(36, 67))
            until_time = update.message.date + datetime.timedelta(seconds=ban_sec)
            can_send_messages = False
            can_send_media_messages = False
            can_send_other_messages = False
            can_add_web_page_previews = False
            success = bot.restrict_chat_member(chatid, user_id, until_time, can_send_messages,
                                            can_send_media_messages, can_send_other_messages, can_add_web_page_previews)
            if success:
                update.message.reply_text('Congratulation! you have been banned for {} seconds~'.format(str(ban_sec)))
            else:
                update.message.reply_text('受到电磁干扰...')
    else:
        update.message.reply_text('可惜我失去了力量...')


def fake_banmyself(bot, update):
    chatID = update.message.chat_id
    if chatID > 0:
        update.message.reply_text("你在嗦什么，我怎么听不懂。")
    else:
        update.message.reply_text("Congratulation! Now, you are banned.")


def say_hello(bot, update):
    # chatId = update.message.chat_id
    replyText = "Hello.\n"
    update.message.reply_text(replyText,
                              parse_mode='Markdown')


def hello_to_all(bot, update):
    # chatId = update.message.chat_id
    replyText = '大家好，我是一只只会嗦hello的咸鱼.\n'
    bot.send_message(update.message.chat_id, replyText)


def record(bot, update):
    replyText = fiddler(update.message.text)
    bot.send_message(update.message.chat_id, replyText)


def real_record(bot, update):
    chatid = update.message.chat_id
    if chatid in chat_id_list:
        bot.send_message(update.message.chat_id, '好累啊,休息休息...')
        chat_id_list.remove(chatid)
    else:
        bot.send_message(update.message.chat_id, '复读机!复读机!')
        chat_id_list.append(chatid)

    # replyText = fiddler(update.message.text)
    # while conti:
    #    bot.send_message(update.message.chat_id, replyText)
    # update.message.reply_text('这个功能目前不可控，暂不开放')


def all_links(bot, update):
    global main_links, friend_links
    links_list = ["链接: "]
    for link in main_links:
        links_list.append(main_links[link] + ': ' + link)
    links_list.append("\n友链: ")
    for link in friend_links:
        links_list.append(friend_links[link] + ': ' + link)
    replyText = '\n'.join(links_list)
    update.message.reply_text(replyText)


def all_questions(bot, update):
    global question_keys, questions
    if update.message.chat_id > 0:
        text_list = ['问题: ']
        for que in question_keys:
            text_list.append(que + ': ' + questions[que])
        replyText = '\n'.join(text_list)
    else:
        replyText = '因为问题列表可能很长，请在私聊中查看哦。'
    update.message.reply_text(replyText)


def all_answers(bot, update):
    global question_keys, questions, answers
    text_list = ['所有问题和答案: ']
    for que in question_keys:
        if que in answers:
            ans = answers[que]
        else:
            ans = '还没有答案哦. '
        text_list.append(que + '. Q: ' + questions[que]
                         + '\nA: ' + ans + '\n')
    replyText = '\n'.join(text_list)
    update.message.reply_text(replyText)


def answer(bot, update, args):
    global question_keys, questions, answers
    num = str(args[0])
    logging.debug(num)
    if num in question_keys:
        replyText = '第{}个问题: \nQ: {}\nA: {}'.format(num, questions[num], answers[num])
    else:
        replyText = '请输入正确的号码哦. '
    update.message.reply_text(replyText)


def question(bot, update):
    global question_keys, questions, answers
    num = random.choice(question_keys)
    replyText = '第{}个问题: \nQ: {}\nA: {}'.format(num,
                                                questions[num], answers[num])
    update.message.reply_text(replyText)


def search(bot, update, search_name):
    if update.message.chat_id < 0:
        replyText = ('[@{}](tg://user?id={})    \n'.format(update.message.from_user.first_name,
                                                           update.message.from_user.id))
    else:
        replyText = ''
    replyText = replyText + '这是为您从 {} 找到的: \n'.format(search_name)
    return replyText


def encode_url_words(l):
    return utils.url_encode(' '.join(l))


def google(key_words):
    return '  ** [{}](https://www.google.com/search?q={}) **'.format(' '.join(key_words), encode_url_words(key_words),
                                                                     parse_mode='Markdown')


def baidu(key_words):
    return '  ** [{}](https://www.baidu.com/s?wd={}) **'.format(' '.join(key_words), encode_url_words(key_words),
                                                                parse_mode='Markdown')


def ddg(key_words):
    return '  ** [{}](https://duckduckgo.com/?q={}) **'.format(' '.join(key_words), encode_url_words(key_words),
                                                               parse_mode='Markdown')


def bing(key_words):
    return '  ** [{}](https://bing.com/search?q={}) **'.format(' '.join(key_words), encode_url_words(key_words),
                                                               parse_mode='Markdown')


def search_google(bot, update, args):
    if args.__len__() != 0:
        replyText = search(bot, update, 'Google') + google(args)
    else:
        replyText = '请输入关键字. '
    bot.send_message(update.message.chat_id, replyText, parse_mode='Markdown')


def search_baidu(bot, update, args):
    if args.__len__() != 0:
        replyText = search(bot, update, '百毒') + baidu(args)
    else:
        replyText = '请输入关键字. '
    bot.send_message(update.message.chat_id, replyText, parse_mode='Markdown')


def search_ddg(bot, update, args):
    if args.__len__() != 0:
        replyText = search(bot, update, 'DuckDuckGo') + ddg(args)
    else:
        replyText = '请输入关键字. '
    bot.send_message(update.message.chat_id, replyText, parse_mode='Markdown')


def search_bing(bot, update, args):
    if args.__len__() != 0:
        replyText = search(bot, update, '巨硬御用的Bing') + bing(args)
    else:
        replyText = '请输入关键字. '
    bot.send_message(update.message.chat_id, replyText, parse_mode='Markdown')


def boot(bot, update):
    update.message.reply_text('早上好，今天也是元气满满的一天哦！')


def sleep(bot, update):
    update.message.reply_text('晚安，明天醒来就能看到我哦！')


def chat(bot, update, args):
    message = ''.join(args)
    if message.__len__ != 0:
        update.reply_text(turing.interact(message))
    else:
        chatid = update.message.chat_id
        if chatid in turing_chat_list:
            update.message.reply_text('累了~不聊啦~')
            chat_id_list.remove(chatid)
        else:
            update.message.reply_text('陪你聊聊呗~')
            chat_id_list.append(chatid)


def read_message(bot, update):
    message = update.message.text
    sticker = update.message.sticker
    chatid = update.message.chat_id
    if chatid in chat_id_list:
        bot.send_message(chatid, message)
        bot.send_sticker(chatid, sticker)
    elif chatid in turing_chat_list:
        update.reply_text(turing.interact(message))


def main(path):
    global data_dict, QnA_dict, links_dict, about_str, \
        question_keys, questions, answers, main_links, friend_links
    # working_path = path
    data_dict = load_json()

    QnA_dict = data_dict["questions_and_answers"]

    question_keys = [key for key in QnA_dict["questions"]]
    questions = QnA_dict["questions"]
    answers = QnA_dict["answers"]

    links_dict = data_dict["links"]
    main_links = links_dict["main_links"]
    friend_links = links_dict["friend_links"]

    updater = Updater(token=TOKEN)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text, read_message))
    dp.add_handler(CommandHandler('banmyself', banmyself))
    dp.add_handler(CommandHandler('fake_banmyself', fake_banmyself))
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('say_hello', say_hello))
    dp.add_handler(CommandHandler('hello_to_all', hello_to_all))
    dp.add_handler(CommandHandler('record', record))
    dp.add_handler(CommandHandler('real_record', real_record))
    dp.add_handler(CommandHandler('all_links', all_links))
    dp.add_handler(CommandHandler('all_questions', all_questions))
    dp.add_handler(CommandHandler('all_answers', all_answers))
    dp.add_handler(CommandHandler('answer', answer, pass_args=True))
    dp.add_handler(CommandHandler('question', question))
    dp.add_handler(CommandHandler('google', search_google, pass_args=True))
    dp.add_handler(CommandHandler('search_baidu', search_baidu, pass_args=True))
    dp.add_handler(CommandHandler('ddg', search_ddg, pass_args=True))
    dp.add_handler(CommandHandler('bing', search_bing, pass_args=True))
    dp.add_handler(CommandHandler('boot', boot))
    dp.add_handler(CommandHandler('poweroff', sleep))
    dp.add_handler(CommandHandler('shutdown', sleep))
    dp.add_handler(CommandHandler('chat', chat))
    dp.add_handler(CommandHandler('weather', weather_qy, pass_args=True))
    updater.start_polling()


if __name__ == '__main__':
    path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(path)
    main(path)
