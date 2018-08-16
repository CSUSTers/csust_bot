from itertools import starmap, repeat
from operator import add, mod
from functools import reduce


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
    _ck_st = r"^{}\s*\(\s*{}\s*\)$".format(_ck_function_name, str.join(r',\s*', [r'(.*)']))
    _ck_statment = r"$1.build_new_attribute($2).reduce_to_object(eval($2)) if eval($2) is not None else None"
    @staticmethod
    def creat_macro_pattern(name, arg_ct):
        pattern = r"^{}\s*\(\s*{}\s*\)$".format(name, str.join(r',\s*', [r'(.*)'] * arg_ct))
        return pattern

    def __init__(self):
        JSONBuilder.__init__(self)
        for f in self.fields:
            self.build_new_attribute(f)
        self._access_field(0).reduce_to_object(0) 
    
    def add_text(self, text:str):
        self._access_field(1).build_new_attribute("inputText")  \
                            .build_new_attribute("text")        \
                            .reduce_to_object(text)
        return self
    
    def add_image(self, url:str):
        self._access_field(1).build_new_attribute("inputImage") \
                             .build_new_attribute("url")        \
                             .reduce_to_object(url)
        self._access_field(0).reduce_to_object(max(self._access_field(0).build(), 1))
        return self

    def add_vedio(self, url:str):
        self._access_field(1).build_new_attribute("inputMedia") \
                             .build_new_attribute("url")        \
                             .reduce_to_object(url)
        self._access_field(0).reduce_to_object(max(self._access_field(0).build(), 2))
        return self
        
    def add_location(self, city:str, province=None, street=None):
        self_info = self._access_field(1).build_new_attribute("selfInfo") 
        self_info.build_new_attribute("city").reduce_to_object(city)
        self_info.build_new_attribute("province").reduce_to_object(eval("province")) if eval("province") is not None else None
        self_info.build_new_attribute("street").reduce_to_object(eval("street")) if eval("street") is not None else None
        return self

    def add_userinfo(self, apiKey, userId, groupId=None, userIdName=None):
        user_info = self._access_field(2)
        user_info.build_new_attribute("apiKey").reduce_to_object(eval("apiKey")) if eval("apiKey") is not None else None
        user_info.build_new_attribute("userId").reduce_to_object(eval("userId")) if eval("userId") is not None else None
        user_info.build_new_attribute("groupId").reduce_to_object(eval("groupId")) if eval("groupId") is not None else None
        user_info.build_new_attribute("userIdName").reduce_to_object(eval("userIdName")) if eval("userIdName") is not None else None
        return self

    def _access_field(self, fieldno:int) -> JSONBuilder:
        return self[self.fields[fieldno]]