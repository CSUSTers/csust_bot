import requests
from configparser import ConfigParser
from random import randrange
from sys import stderr
from functools import partial
from operator import getitem
from JSONBuilder import RequestBuilder
import re

errlog = partial(print, file=stderr, flush=True)
template = '''{
    "reqType": %s,
    "perception": {
        %s
        "selfInfo": {
        }
    },
    "userInfo": {
        "apiKey": "%s",
        "userId": "%s"
    }
}'''

"""
机器人类。
你可以与他进行交互。
"""
class turing_robot:
    # static attributes.
    textPerception = '"inputText": {"text": "%s"},'
    photoPerception = '"inputImage": {"url": "%s"},'
    mediaPerception = '"inputMedia": {"url": "%s"},'
    photo_utl_re = re.compile(r'^(https?|ftp)://.*\.(jpg|png|jpeg|ico|gif|svg|webp)$')


    def __init__(self, userid = None, config_file = 'robotconf.ini'):
        c = ConfigParser()
        self.userid = userid or "DoesMadeInAbyssTodayUpdated"
        self.errno = 0
        try:
            c.read_file(open(config_file))
            self.interface_address = c['API']['interface_address']
            self.apikey = c['API']['apikey']
        except IOError as e:
            errlog("IOError: {}, 可能是配置文件不存在。".format(e))
            self.errno &= 0x01
        except KeyError as e:
            errlog("KeyError: {}，可能是配置文件有误。".format(e))
            self.errno &= 0x02

        self.temp = template % ("%d", "%s", self.apikey, self.userid)

    def make_request(self, text=None, photo=None, media=None) -> requests.models.Response:
        """
        请求接口，使用指定的文字、图片或者音频，创建一个 HTTP 请求。
        """
        payloads = ""
        if text is not None:
            payloads += self.textPerception % (text)
            reqtype = 0
        if photo is not None:
            payloads += self.photoPerception % (photo)
            reqtype = 1
        if media is not None:
            payloads += self.mediaPerception % (media)
            reqtype = 2
        if len(payloads) > 0:
            r = requests.post(self.interface_address, data=(self.temp % (reqtype, payloads)).encode('utf-8'))
            return r

    def make_responce(self, text=None, photo=None, media=None):
        """
        更加简洁的接口：给予输入，直接获取它的输出（封装于 robot_response 类中）
        """
        r = self.make_request(text, photo, media)
        retjson = r.json()
        results = retjson['results']
        return robot_response(results)

    def interact(self, quesion: str) -> str:
        """
        更更加简洁的接口：给予输入，不管返回什么，统统转化为字符串！
        暂未实现音频功能。
        """
        if self.photo_utl_re.match(quesion) is not None:
            return self.make_responce(photo=quesion).get_response_content()
        else:
            return self.make_responce(text=quesion).get_response_content()
    
class robot_response:
    def __init__(self, results):
        self.grouped_data = []
        self.data = None
        for r in results:
            if r['groupType'] == 0:
                self.data = (r['resultType'], str.join('\n', r['values'].values()))
            else:
                self.grouped_data.append((r['resultType'], str.join('\n', r['values'].values())))

    def get_response_content(self) -> str:
        if self.data is not None:
            return self.data[1]
        else:
            # 我在这里默认了 groupType 只有 0 或者 1 两种状况。
            return str.join('\n\n', map(lambda o: getitem(o, 1), self.grouped_data))
    
    def get_response(self):
        if self.data is not None:
            return self.data
        else:
            return self.grouped_data


