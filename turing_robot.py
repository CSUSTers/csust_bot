import requests
from configparser import ConfigParser
from random import randrange
from sys import stderr
from functools import partial
from operator import getitem
from utils import RequestBuilder
from json import dumps
from copy import deepcopy

from config import TuringBotConfig
import re

errlog = partial(print, file=stderr, flush=True)

"""
机器人类。
你可以与他进行交互。
"""


class turing_robot:
    # static attributes.
    photo_utl_re = re.compile(
        r'^(https?|ftp)://.*\.(jpg|png|jpeg|ico|gif|svg|webp)$')

    def __init__(self, userid=None):
        self.userid = userid or "DoesMadeInAbyssTodayUpdated"
        self.errno = 0
        try:
            self.interface_address = TuringBotConfig.api_address
            self.apikey = TuringBotConfig.apikey
        except AttributeError as e:
            errlog("AttributeError: {}，可能是配置文件中相应的类有一些问题。".format(e))
            self.errno &= 0x01

        self.request_json_prototype = RequestBuilder().add_userinfo(self.apikey, self.userid)
        self.request_json = deepcopy(self.request_json_prototype)

    def make_request(self):
        r = requests.post(self.interface_address, data=dumps(
            self.request_json.build()).encode('utf-8'))
        self.request_json = deepcopy(self.request_json_prototype)
        sc = r.status_code
        if sc == 200:
            return r
        else:
            r.close()
            raise requests.HTTPError("HTTP ERROR: {}".format(sc))

    def make_responce(self):
        """
        更加简洁的接口：给予输入，直接获取它的输出（封装于 robot_response 类中）
        """
        r = self.make_request()
        retjson = r.json()
        results = retjson['results']
        return robot_response(results)

    def interact(self, quesion: str) -> str:
        """
        更更加简洁的接口：给予输入，不管返回什么，统统转化为字符串！
        暂未实现音频功能。
        """
        try:
            if self.photo_utl_re.match(quesion) is not None:
                self.request_json.add_image(quesion)
                return self.make_responce().get_response_content()
            else:
                self.request_json.add_text(quesion)
                return self.make_responce().get_response_content()
        except requests.HTTPError as he:
            errlog("err: {}".format(he))
            return "请求失败：{}".format(he)


class robot_response:
    def __init__(self, results):
        self.grouped_data = []
        self.data = None
        for r in results:
            if r['groupType'] == 0:
                self.data = (r['resultType'], str.join(
                    '\n', r['values'].values()))
            else:
                self.grouped_data.append(
                    (r['resultType'], str.join('\n', r['values'].values())))

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
