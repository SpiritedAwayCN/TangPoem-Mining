from dearpygui.simple import *
from dearpygui.core import *
from dearpygui.demo import *
from functools import cmp_to_key

from .poem.query import query_final


def poem_cmp(a, b):
    a, b = a[1], b[1]
    if abs(a[0] - b[0]) <= 1e-6:
        return b[1] - a[1]
    else:
        return b[0] - a[0]

class BasePublisher(object):
    def __init__(self,name):
        self.readers = []
        self.name=name
    
    def subscribeReader(self, reader, author, keywords, hit):
        self.readers.append(reader)
        return query_final(keywords, hit, author)

    def unsubscribeReader(self, reader):
        self.readers.remove(reader)
        return self

    def notifyReader(self,author, poem):
        pass

class Publisher(BasePublisher):
    def __init__(self,name):
        BasePublisher.__init__(self,name)
        
    def notifyReader(self, author, poem):
        pass

class BaseReader(object):

    def __init__(self, name=None):
        # BaseReader 的初始化方法
        self.name = name
        self.sym_set = []
        self.poems = []
        
    def subscribeToPublisher(self, publisher, keywords, author=None, hit=True):
        
        self.publisher = publisher
        self.keywords = keywords
        self.author = author
        self.hit = hit

        # TODO Reader向Publisher订阅
        r = publisher.subscribeReader(self, author, keywords, hit)
        if not r is None:
            self.sym_set, res = r
            self.poems = sorted(res, key=cmp_to_key(poem_cmp))
            # self.poems = list(map(lambda x: res[x], self.poems))
        # print(self.poems)
        
    def unsubscribeToPublisher(self):
        if self.publisher is None:
            return
        self.publisher.unsubscribeReader(self)
        self.publisher = None
    
    def receivePoem(self, publisher, poem , author):
        pass
    
    def printStatistics(self):
        # 打印消息
        pass

class Reader(BaseReader):

    def __init__(self, _name):
        BaseReader.__init__(self, _name)
        
    def receivePoem(self, publisher, poem, author):
        pass

    def __str__(self) -> str:
        return f'{self.author if self.author else "[不限]"}: {", ".join(self.keywords)}'