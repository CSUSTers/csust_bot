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
    _ck_st = "self\._check_and_set\s*\(\s*(.*),\s*(.*)\s*\)"
    _ck_replace = "$1.build_new_attribute($2).reduce_to_object(eval($2)) if eval($2) is not None else None"
            

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
        self._access_field(0).reduce_to_object(max(self._access_field(0).build, 1))
        return self

    def add_vedio(self, url:str):
        self._access_field(1).build_new_attribute("inputMedia") \
                             .build_new_attribute("url")        \
                             .reduce_to_object(url)
        self._access_field(0).reduce_to_object(max(self._access_field(0).build, 2))
        return self
        
    def add_location(self, city:str, province=None, street=None):
        self_info = self._access_field(1).build_new_attribute("selfInfo") 
        self_info.build_new_attribute("city").reduce_to_object(city)
        self_info.build_new_attribute("province").reduce_to_object(eval("province")) if eval("province") is not None else None
        self_info.build_new_attribute("street").reduce_to_object(eval("street")) if eval("street") is not None else None
        return self

    def add_userinfo(self, apikey, userid, groupId=None, userIdName=None):
        user_info = self._access_field(2)
        user_info.build_new_attribute("apikey").reduce_to_object(eval("apikey")) if eval("apikey") is not None else None
        user_info.build_new_attribute("userid").reduce_to_object(eval("userid")) if eval("userid") is not None else None
        user_info.build_new_attribute("groupId").reduce_to_object(eval("groupId")) if eval("groupId") is not None else None
        user_info.build_new_attribute("userIdName").reduce_to_object(eval("userIdName")) if eval("userIdName") is not None else None
        return self

    def _access_field(self, fieldno:int) -> JSONBuilder:
        return self[self.fields[fieldno]]

    
    
    
    
    