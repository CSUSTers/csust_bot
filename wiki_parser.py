from bs4 import BeautifulSoup
from bs4.element import Comment
from requests import post
from operator import add
from functools import reduce
from itertools import takewhile
from collections.abc import Iterable
from re import match

def tag_markdownify(tag):
    ret = ""
    if issubclass(type(tag), Comment):
        return ret
    if issubclass(type(tag), str):
        ret += tag.strip()
        return ret
    if 'mw-editsection' in tag.get('class', [])  :
        return ret
    if tag.name == 'li':
        ret += "- "
    if tag.name == 'a' and tag.get('href', None) is not None:
        ret += "["
    if tag.name == 'ol':
        ret += make_ordered_list(tag)
        return ret
    if match(r"h[0-9]", tag.name):
        ret += "#" * int(tag.name[1]) + " "

    for i in map(tag_markdownify, tag.childGenerator()):
        ret += i

    if tag.name == 'a' and tag.get('href', None) is not None:
        ret += f"]({tag['href']})  "
    if tag.name == 'p':
        ret += "  "
    if tag.name != 'a':
        ret += '\n'
    return ret

def make_ordered_list(tag):
    ret = ""
    list_count = 0
    for c in tag.childGenerator():
        if getattr(c, 'name', None) == 'li':
            list_count += 1
            ret += f"{list_count}. {reduce(add, (tag_markdownify(cs) for cs in c.childGenerator()))}\n"
        else:
            ret += tag_markdownify(c)
    return ret

def join_iterable(m):
    if issubclass(type(m), Iterable):
        for x in m:
            for y in join_iterable(x):
                yield y
    else:
        yield m

class wiki_request:
    content_tag_name = 'div'
    content_class_name = 'mw-parser-output'
    def __init__(self, keyword, lang='zh'):
        self.r = post(f"https://{lang}.wikipedia.org/", data={'search': keyword})
        if self.r.status_code != 200:
            raise RuntimeError(f"HTTP request failed, fail code: {self.r.status_code}")
        else:
            self.soup = BeautifulSoup(self.r.text, 'html.parser')
            self.content = self.soup.find(wiki_request.content_tag_name, class_=wiki_request.content_class_name)
        self.r.close()

    def get_brief_conent(self):
        return self.content.p.text

    def get_disambiguation_contnet(self):
        return tag_markdownify(self.content)
        
 
tester = '''
<html>
<h1> title1 </h1>
<h2> title2 </h2>
<h6> title6 </h6>
<a href="foo.bar"> foo.bar </a>
<p> foo </p>
<ol>
  <li>Coffee</li>
  <li>Tea</li>
  <li>Milk</li>
</ol>
</html>
'''

tc = BeautifulSoup(tester, 'html.parser')
test = lambda: reduce(add, join_iterable(make_ordered_list(tc)), "")
if __name__ == '__main__':
    w = wiki_request("haskell", lang='en')
    with open('/home/hill/Developer/csust_bot/foo.md', 'w') as foo:
       print(w.get_disambiguation_contnet(), file=foo)