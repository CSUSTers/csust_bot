from itertools import starmap, repeat
from operator import add, mod
from functools import reduce
from telegram.ext import Updater
from telegram import error, Bot
from googletrans import Translator
from re import compile
import re

tr = Translator()
trans_re = compile(r"^([\S]*)\s*(\'[\w\-]*\')?\s*(.*)", re.M|re.U|re.DOTALL)

def url_encode(s: str):
    """
    将字符串编码为搜索引擎需求的形式(%XX)。
    param {s} string to encode.
    ret the encoded string.

    example
    < 'flip flappers'
    > '%66%6c%69%70%20%66%6c%61%70%70%65%72%73'

    < '\01\02'
    > '%01%02'

    < "来自深渊今天更新了吗？"
    > "%e6%9d%a5%e8%87%aa%e6%b7%b1%e6%b8%8a%e4%bb%8a%e5%a4%a9%e6%9b%b4%e6%96%b0%e4%ba%86%e5%90%97%ef%bc%9f"
    """
    return reduce(add,
                  starmap(
                      mod, zip(repeat("%%%.2x"),
                               s.encode("utf-8"))),
                  "")


class JSONBuilder:
    def __init__(self):
        self.data = {}

    def __getitem__(self, key):
        if type(self.data) is dict:
            return self.data.get(key, None)
        return None

    def __setitem__(self, key, vaule):
        return self.data.setdefault(key, vaule)

    def build_new_attribute(self, attr_name):
        if type(self.data) is dict and attr_name not in self.data:
            self[attr_name] = JSONBuilder()
        return self[attr_name]

    def reduce_to_object(self, o):
        self.data = o

    def build(self):
        if type(self.data) is dict:
            ret = {}
            for (k, v) in self.data.items():
                ret[k] = v.build()
            return ret
        else:
            return self.data


class RequestBuilder(JSONBuilder):
    fields = ["reqType", "perception", "userInfo"]

    # ck_marco -- 用文本编辑器的替换功能实现类似 C 语言的 macro。(什么鬼！)
    _ck_function_name = r"_check_and_set"
    _ck_arg_ct = 2
    _ck_st = r"^{}\s*\(\s*{}\s*\)$".format(_ck_function_name,
                                           str.join(r',\s*', [r'(.*)']))
    _ck_statment = r"$1.build_new_attribute($2).reduce_to_object(eval($2)) if eval($2) is not None else None"

    @staticmethod
    def creat_macro_pattern(name, arg_ct):
        pattern = r"^{}\s*\(\s*{}\s*\)$".format(name,
                                                str.join(r',\s*', [r'(.*)'] * arg_ct))
        return pattern

    def __init__(self):
        JSONBuilder.__init__(self)
        for f in self.fields:
            self.build_new_attribute(f)
        self._access_field(0).reduce_to_object(0)

    def add_text(self, text: str):
        self._access_field(1).build_new_attribute("inputText")  \
            .build_new_attribute("text")        \
            .reduce_to_object(text)
        return self

    def add_image(self, url: str):
        self._access_field(1).build_new_attribute("inputImage") \
                             .build_new_attribute("url")        \
                             .reduce_to_object(url)
        self._access_field(0).reduce_to_object(
            max(self._access_field(0).build(), 1))
        return self

    def add_vedio(self, url: str):
        self._access_field(1).build_new_attribute("inputMedia") \
                             .build_new_attribute("url")        \
                             .reduce_to_object(url)
        self._access_field(0).reduce_to_object(
            max(self._access_field(0).build(), 2))
        return self

    def add_location(self, city: str, province=None, street=None):
        self_info = self._access_field(1).build_new_attribute("selfInfo")
        self_info.build_new_attribute("city").reduce_to_object(city)
        self_info.build_new_attribute("province").reduce_to_object(
            eval("province")) if eval("province") is not None else None
        self_info.build_new_attribute("street").reduce_to_object(
            eval("street")) if eval("street") is not None else None
        return self

    def add_userinfo(self, apiKey, userId, groupId=None, userIdName=None):
        user_info = self._access_field(2)
        user_info.build_new_attribute("apiKey").reduce_to_object(
            eval("apiKey")) if eval("apiKey") is not None else None
        user_info.build_new_attribute("userId").reduce_to_object(
            eval("userId")) if eval("userId") is not None else None
        user_info.build_new_attribute("groupId").reduce_to_object(
            eval("groupId")) if eval("groupId") is not None else None
        user_info.build_new_attribute("userIdName").reduce_to_object(
            eval("userIdName")) if eval("userIdName") is not None else None
        return self

    def _access_field(self, fieldno: int) -> JSONBuilder:
        return self[self.fields[fieldno]]


class _secGetter:
    def getDigit(self, s: str):
        s = ''.join(re.split('[a-zA-Z]', s))
        if s:
            try:
                return int(eval(s))
            except:
                return 0
        else:
            return 0

    def month2sec(self, s: str):
        return self.getDigit(s)*30*24*60*59

    def day2sec(self, s: str):
        return self.getDigit(s)*24*60*59

    def hour2sec(self, s: str):
        return self.getDigit(s)*60*59

    def min2sec(self, s: str):
        return self.getDigit(s)*59

    def getOneSec(self, s: str):
        return self.getDigit(s)

    def format2sec(self, s: str):
        secs = 0
        l = s.split(':')
        if not len(l) in [2, 3]:
            return 0
        for _1s in l:
            secs *= 60
            secs += self.getDigit(_1s)
        return secs

    def get(self, list):
        secs = 0
        for l in list:
            if l[-1] in ['M', 'm']:
                secs += self.month2sec(l[:-1])
            elif l[-1] in ['D', 'd']:
                secs += self.day2sec(l[:-1])
            elif l[-1] in ['H', 'h']:
                secs += self.hour2sec(l[:-1])
            elif l[-1] in ['i', 'I']:
                secs += self.min2sec(l[:-1])
            elif l[-3:].upper() == 'MIN':
                secs += self.min2sec(l[:-3])
            elif l[-1] in ['S', 's']:
                if l[:-1] == '-1':
                    secs -= 1
                else:
                    secs += self.getOneSec(l[:-1])
            elif l.isdigit():
                secs += int(l)
            else:
                secs += self.format2sec(l)
        return secs


SecGetter = _secGetter()


"""
感觉下面的这段代码就很流水线化生产
"""

search_dict = {
    'google': 'https://www.google.com/search?q={q}',
    'bing': 'https://bing.com/search?q={q}',
    'ddg': 'https://duckduckgo.com/?q={q}',
    'bd': 'https://www.baidu.com/s?wd={q}'
}


def search(bot, update, search_name):
    if update.message.chat_id < 0:
        replyText = ('[@{}](tg://user?id={})    \n'.format(update.message.from_user.first_name,
                                                           update.message.from_user.id))
    else:
        replyText = ''
    replyText = replyText + '这是为您从 {} 找到的: \n'.format(search_name)
    return replyText


def encode_url_words(s):
    # return url_encode(' '.join(l))
    return url_encode(s)


def get_search_url(name, keyswords_list):
    key_words = ' '.join(keyswords_list)
    base = '  ** [{words}](' + search_dict[name] + ') **'
    return base.format(words=key_words, q=encode_url_words(key_words))


def search_google(bot, update, args):
    if args:
        replyText = search(bot, update, 'Google') + \
            get_search_url('google', args)
    else:
        replyText = '请输入关键字. '
    bot.send_message(update.message.chat_id,
                     replyText, parse_mode='Markdown')


def search_baidu(bot, update, args):
    if args:
        replyText = search(bot, update, '百毒') + get_search_url('bd', args)
    else:
        replyText = '请输入关键字. '
    bot.send_message(update.message.chat_id,
                     replyText, parse_mode='Markdown')


def search_ddg(bot, update, args):
    if args:
        replyText = search(bot, update, 'DuckDuckGo') + \
            get_search_url('ddg', args)
    else:
        replyText = '请输入关键字. '
    bot.send_message(update.message.chat_id,
                     replyText, parse_mode='Markdown')


def search_bing(bot, update, args):
    if args:
        replyText = search(bot, update, '巨硬御用的Bing') + \
            get_search_url('bing', args)
    else:
        replyText = '请输入关键字. '
    bot.send_message(update.message.chat_id,
                     replyText, parse_mode='Markdown')


def goltrans(bot, update, args):
    global tr
    text = update.message.text
    if args:
        lang = ''
        matcher = trans_re.match(text)
        if matcher is not None:
            groups = matcher.groups()
            lang = groups[1].strip("'").lower() if groups[1] else ''
            text = groups[2]
            if not text:
                update.message.reply_text("嗦点什么呀，同学")
        elif args[0].startswith("'") and args[0].endswith("'"):
            lang = args[0].strip("'").lower()
            text = ' '.join(args[1:])
        else:
            lang = ''
            text = ' '.join(args)

        if not lang:
            lang = 'zh-cn'
            for c in text:
                if '\u4e00' <= c <= '\u9fff':
                    lang = 'en'
                    break
        
        try:
            if lang:
                text = tr.translate(text, dest=lang).text
            else:
                text = tr.translate(text).text
        except Exception as e:
            text = '出错了？？？'
            print(e)
            tr = Translator()
        update.message.reply_text(text)
    else:
        update.message.reply_text('想翻译什么呢~\n(私聊中使用 /translangs 可以查看目标语言代码哦)')

        
def for_eachsub(pattern, haystack, fn):
    """
    the enhanced replace method.  
    instead of passing a expand format string as parameter,
    it accept a function which accept a `re.match` object, 
    returning a expand format string.

    simple:
    ```
    < ("foo", "foobarfoo", lambda _: "Foo")
    > "FoobarFoo"
    ```

    a more complex example is the `parse_formal_time_expression` in `timeval`.
    """
    if isinstance(pattern, str):
        pattern = compile(pattern)

    pos = 0
    m = pattern.search(haystack, pos)
    while m:
        haystack = pattern.sub(
            fn(m), haystack, 1)
        pos = m.end()
        m = pattern.search(haystack, pos)

    return haystack

