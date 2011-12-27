#!/usr/bin/env python2
# -*- coding:utf8 -*-
from google.appengine.api import urlfetch

def random():
    try:
        content = urlfetch.fetch('http://www.commandlinefu.com/commands/random/plaintext').content
    except urlfetch.DownloadError:
         return None
    return content
