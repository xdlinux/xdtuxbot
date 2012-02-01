# -*- coding:utf8 -*-
from config import WOEID
import urllib
from elementtree.ElementTree import parse

class FetchError(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)

count = 0

WEATHER_URL = "http://weather.raychou.com/?/detail/%s/count_2/rss"

def weather():
    """docstring for weather"""
    url = WEATHER_URL %  WOEID
    rss = parse(urllib.urlopen(url)).getroot()
    fc = rss.findtext('channel/item/description').encode("utf-8")
    return fc

if __name__ == "__main__":
    weather()
