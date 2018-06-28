from bs4 import BeautifulSoup
from requests import post
from operator import add
from functools import reduce
from itertools import takewhile

class wiki_request:
    content_tag_name = 'div'
    content_class_name = 'mw-parser-output'
    def __init__(self, keyword, lang='zh'):
        self.r = post(f"https://{lang}.wikipedia.org/", data={'search': keyword})
        if self.r.status_code != 200:
            raise RuntimeError(f"HTTP request failed, fail code: {self.r.status_code}")
        else:
            self.soup = BeautifulSoup(self.r.text, "html5lib")
            self.content = self.soup.find(wiki_request.content_tag_name, class_=wiki_request.content_class_name)
        self.r.close()

    def get_brief_conent(self):
        return self.content.p.text

    def get_disambiguation_contnet(self):
        def _accumer(a, n):
            return f"{a}  \n[{n.a['title']}]({n.a['href']}) -> {n.text}"
        htitles = self.content.find_all('h2')
        for htitle in htitles:
            try:
                yield f'### {htitle.span.text}  \n'
                yield reduce(add, [reduce(_accumer, x.find_all('li'), "") for x in takewhile(lambda x: x.name != 'h2', htitle.next_siblings) if x.name == 'ul'], "") + "  \n"
            except AttributeError:
                pass
