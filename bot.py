#!/usr/bin/env python3

"""
commands:
say_hello - 我是一只只会嗦hello的咸鱼
hello_to_all - Say hello to all group members
record - 人类的本质就是复读机，Bot也是一样的
real_record - 复读机...复读机...复读机的开关
no_sticker - [num] 聊天时仅保留num个sticker，默认为0，小于零或大于100退出no_sticker模式
gtranslate - ['lang'] [text] 咕果翻译
translangs - 查询咕果翻译语言对应代码(私聊可用)
google - <Key Words> Search Google...
ddg - <Key Words> Search DuckDuckGo...
bing - <Key Words> Search Bing...
weather - <CityName> 查询天气
all_links - 这里有一些链接，如果本校同学想要添加友链也可以联系哦
all_questions - 显示所有的问题
all_answers - 显示所有的问题和答案
answer - <Num>  回答指定的问题
question - 随机问题
search_baidu - <Key Words> 在百毒搜索...
banmyself - 把自己ban掉[36,66]秒
ban - 我就是要滥权！
fake_banmyself - 虚假的ban自己

----------
"""
import datetime
from uuid import uuid4
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler, CallbackQueryHandler, InlineQueryHandler
from telegram import error, Bot, Chat, User, Message, ChatMember, Sticker, InlineKeyboardMarkup, InlineKeyboardButton, InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from config import TOKEN
from weather_query import weather_qy, wther
from utils import SecGetter

import json
import random
import logging
import utils
import requests
import sys, os
from ban_user_tools import BanUser
from utils import (search_google, search_bing, search_baidu, search_ddg, goltrans)


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
record_chat_id_list = []

# for turing_chat
#turing = turing_robot()
#turing_chat_list = []

# del stkers
no_stker_chat_dict = {}
stker_dict = {}


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


def ban_user(bot, update, user):
    user_id = user.id
    if update.message.reply_to_message:
        message = update.message.reply_to_message
    else:
        message = update.message
    cmd_list = update.message.text.split()[1:]
    long_long_time = 0
    if cmd_list:
        long_long_time = SecGetter.get(cmd_list)
    chatid = update.message.chat_id
    if update.message.chat.type == 'private':
        update.message.reply_text('我觉得布星~')
    elif bot.get_chat_member(chatid, bot.id).status == 'administrator':
        if bot.get_chat_member(chatid, user_id).status in ['administrator', 'creator']:
            update.message.reply_text('神秘的力量使我无法满足你的欲望')
        else:
            if 36 < long_long_time < 26240000:
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
                update.message.reply_to_message.reply_text('Congratulations! You have been banned! Now enjoy your ' + str(ban_sec) + ' seconds~')
            else:
                update.message.reply_text('受到电磁干扰...')
    else:
        update.message.reply_text('可惜我失去了力量...')


def banmyself(bot, update):
    ban_user(bot, update, update.message.from_user)


def ban(bot, update):
    if update.message.chat_id > 0:
        update.message.reply_text('你在嗦什么，我怎么听不懂。')
        return
    
    chat_member = bot.get_chat_member(update.message.chat_id, update.message.from_user.id)
    if not (chat_member.can_restrict_members or chat_member.status == 'creator'):
        banmyself(bot, update)
    else:
        message = update.message.reply_to_message
        if not message is None:
            # 被回复用户
            # user_id = message.from_user.id
            user = message.from_user

            ban_user(bot, update, user)
        else:
            update.message.reply_text('你想ban掉谁呢...')


def fake_banmyself(bot, update):
    chatID = update.message.chat_id
    if chatID > 0:
        update.message.reply_text("你在嗦什么，我怎么听不懂。")
    else:
        update.message.reply_text("Congratulation! Now, you are banned.")


def say_hello(bot, update):
    replyText = "Hello.\n"
    update.message.reply_text(replyText,
                              parse_mode='Markdown')


def hello_to_all(bot, update):
    replyText = '大家好，我是一只只会嗦hello的咸鱼.\n'
    bot.send_message(update.message.chat_id, replyText)


def record(bot, update):
    replyText = fiddler(update.message.text)
    bot.send_message(update.message.chat_id, replyText)


def real_record(bot, update):
    chatid = update.message.chat_id
    if chatid in record_chat_id_list:
        bot.send_message(update.message.chat_id, '好累啊,休息休息...')
        record_chat_id_list.remove(chatid)
    else:
        bot.send_message(update.message.chat_id, '复读机!复读机!')
        record_chat_id_list.append(chatid)


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


def boot(bot, update):
    t = '早上好，今天也是元气满满的一天哦！'
    if random.random() < 0.1:
        t = '早上好，今天也是援气满满的一天哦！'
    update.message.reply_text(t)


def sleep(bot, update):
    update.message.reply_text('晚安，明天醒来就能看到我哦！')


def donotsleep(bot, update):
    update.message.reply_text('睡你麻痹起来嗨！')


def no_sticker(bot, update, args):
    mode = 0
    if(len(args) > 0):
        try:
            mode = int(args[0])
        except ValueError:
            mode = 0
    chatid = update.message.chat_id
    if mode < 0 or mode > 100:
        bot.send_message(update.message.chat_id, "Happy time!")
        del no_stker_chat_dict[chatid]
        del stker_dict[chatid]
    else:
        bot.send_message(update.message.chat_id, "Don't send sticker!")
        no_stker_chat_dict[chatid] = mode
        stker_dict[chatid] = []


def read_message(bot, update):
    message = update.message.text
    sticker = update.message.sticker
    chatid = update.message.chat_id
    new_member = update.message.new_chat_members
    if len(new_member) > 0:
        update.message.reply_text('Welcome to this group~')
    elif chatid in record_chat_id_list:
        if(message is not None):
            bot.send_message(chatid, message)
        if(sticker is not None and chatid not in no_stker_chat_dict):
            bot.send_sticker(chatid, sticker)
    if chatid in no_stker_chat_dict and sticker is not None:
        stker_dict[chatid].append(update.message.message_id)
        if len(stker_dict[chatid]) > no_stker_chat_dict[chatid]:
            bot.delete_message(chatid, stker_dict[chatid][0])
            del stker_dict[chatid][0]


def inlinequery(bot, update):
    query = update.inline_query.query
    if query:
        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title = query + " 太强了",
                    input_message_content = InputTextMessageContent("""{name}太强了!
{name}天下第一!
为什么{name}这么强啊(QAQ)!
我什么时候才能有{name}十分之一强啊(TAT)!
我要是有{name}一半强就好了!
{name}带带窝啊!""".format(name=query).strip()
                )
            )
        ]
        update.inline_query.answer(results)


def id(bot, update):
    update.message.reply_text(update.message.chat_id)


def translangs(bot, update):
    if update.message.chat_id < 0:
        update.reply_text('请在私聊回话查询哦～')
    else:
        update.reply_text("""
`zh-cn` : chinese (simplified)
`zh-tw` : chinese (traditional)
`fr` : french
`de` : german
`ja` : japanese
`la` : latin
`ru` : russian
and more...""".strip(), parse_mode='Markdown')


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
    dp.add_handler(MessageHandler(Filters.text|Filters.sticker|Filters.status_update, read_message))
    dp.add_handler(CommandHandler('banmyself', banmyself))
    dp.add_handler(CommandHandler('ban', ban))
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
    dp.add_handler(CommandHandler('id', id))
    dp.add_handler(CommandHandler('poweroff', sleep))
    dp.add_handler(CommandHandler('shutdown', sleep))
    dp.add_handler(CommandHandler('no_sticker', no_sticker, pass_args=True))
    dp.add_handler(CommandHandler('halt', donotsleep))
    dp.add_handler(CommandHandler('weather', weather_qy, pass_args=True))
    dp.add_handler(CommandHandler('gtranslate', goltrans, pass_args=True))
    dp.add_handler(CommandHandler('translangs', translangs))
    dp.add_handler(InlineQueryHandler(inlinequery))
    updater.start_polling()


if __name__ == '__main__':
    path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(path)
    main(path)
