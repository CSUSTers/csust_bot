import requests
from configparser import ConfigParser
from random import randrange
from sys import stderr
from functools import partial

errlog = partial(print, file=stderr)
template = '''{
    "reqType":%s,
    "perception": {
        "inputText": {
            "text": "%s"
        },
        "selfInfo": {
        }
    },
    "userInfo": {
        "apiKey": "%s",
        "userId": "%s"
    }
}'''

class turing_robot:
    def __init__(self, userid = None, config_file = 'robotconf.ini'):
        c = ConfigParser()
        self.userid = userid or randrange(int(1e10))
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
    
    def make_literal_request(self, quesion: str) -> requests.models.Response:
        jsontemp = self.temp % (0, quesion)
        r = requests.post(self.interface_address, data=jsontemp.encode('utf-8'))
        if r.status_code == 200:
            return r
        else:
            raise Exception("HTTP request fail with code:", r.status_code)
    
    def ask(self, quesion:str):
        r = self.make_literal_request(quesion)
        retjson = r.json()
        results = retjson['results']
        retstr = ""
        for res in results:
            retstr += "{%s}\n" % (res['resultType'])
            for k, v in res['values'].items():
                 retstr += "\t[%s]%s\n" % (k, v)
        r.close()
        return retstr
    
        
