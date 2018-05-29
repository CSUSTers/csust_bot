import requests
from configparser import ConfigParser
from random import randrange
from sys import stderr
from functools import partial
from operator import getitem
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
    photo_utl_re = re.compile(r'(https?|ftp)://.*\.(jpg|png|jpeg|ico|gif|bmp)')

    def __init__(self, userid = None, config_file = 'robotconf.ini'):
        c = ConfigParser()
        self.userid = userid or "DoesMadeInAbyssTodayUpdated"
        self.errno = 0
        try:
            c.read_file(open('robotconf.ini'))
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

    """
    创建一个文字聊天的 http request。
    """
    def make_literal_request(self, quesion: str) -> requests.models.Response:
        return self.make_request(text=quesion)
    
    """
    更加简洁的接口：问一句话，获取它的结果（封装于 robot_response 类中）
    """
    def ask(self, quesion:str):
        r = self.make_literal_request(quesion)
        retjson = r.json()
        results = retjson['results']
        return robot_response(results)

    """
    更更加简洁的接口：问一句话，不管返回什么，统统转化为字符串！
    """
    def interactive(self, quesion: str) -> str:
        return self.ask(quesion).get_response_content()
    
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


