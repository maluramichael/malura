import json
from html.parser import HTMLParser
from io import StringIO


class MetaDataHtmlParser(HTMLParser):
    parsed = False
    meta_data = None

    def handle_comment(self, data):
        if self.parsed:
            return

        self.parsed = True
        self.meta_data = json.loads(data)


class LinkParser(HTMLParser):
    links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            HTMLParser.handle_starttag(self, tag, attrs)

            for attr in attrs:
                if attr[0] == 'href':
                    self.links.append(attr[1])


class HtmlStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()