# -*- coding:utf8 -*-
import re
from google.appengine.api import urlfetch

class FetchError(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)

count = 0

def weather():
    global count
    try:
        content = urlfetch.fetch('http://m.baidu.com/tq?area=%E8%A5%BF%E5%AE%89').content
    except urlfetch.DownloadError:
        count += 1
        if count > 5:
            raise FetchError(count)
        else:
            weather()
   
    today=re.findall(r'今\:.*?<',content)[0][:-1]
    today=re.findall(r'白.*?$',today)[0]
    return (today,count)


