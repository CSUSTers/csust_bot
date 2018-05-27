#!/usr/bin/env python3
"""
commands:
say_hello - 我是一只只会嗦hello的咸鱼
hello_to_all - Say hello to all group members
record - 人类的本质就是复读机，Bot也是一样的
all_links - 这里有一些链接，如果本校同学想要添加友链也可以联系哦
all_questions - 显示所有的问题
all_answers - 显示所有的问题和答案
answer - <Num>  回答指定的问题
question - 随机问题
google - <Key Words> Search Google...

----------
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler
from telegram import error, bot
from config import TOKEN

import json
import random
import logging


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
###


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
    update.message.reply_text('This is a bot made by some csusters stadying SE,\n' 
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
    bot.send_message(update.message.chat_id, replyText)


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


def google(key_words):
    return '  ** [{}](https://www.google.com/search?q={}) **'.format(' '.join(key_words), '%20'.join(key_words))


def search_google(bot, update, args):
    if args.__len__() != 0:
        replyText = search(bot, update, 'Google') + google(args)
    else:
        replyText = '请输入关键字. '
    bot.send_message(update.message.chat_id, replyText, parse_mode='Markdown')


def main():
    global data_dict, QnA_dict, links_dict, about_str,\
        question_keys, questions, answers, main_links, friend_links
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
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('say_hello', say_hello))
    dp.add_handler(CommandHandler('hello_to_all', hello_to_all))
    dp.add_handler(CommandHandler('record', record))
    dp.add_handler(CommandHandler('all_links', all_links))
    dp.add_handler(CommandHandler('all_questions', all_questions))
    dp.add_handler(CommandHandler('all_answers', all_answers))
    dp.add_handler(CommandHandler('answer', answer, pass_args=True))
    dp.add_handler(CommandHandler('question', question))
    dp.add_handler(CommandHandler('google', search_google, pass_args=True))
    updater.start_polling()


if __name__ == '__main__':
    main()

