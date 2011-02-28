#!/usr/bin/env python
#coding=utf-8

import re
import urllib2

# 天气预报
def Weather(time):
    url='http://www.weather.com.cn/html/weather/101110101.shtml'

    opener = urllib2.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3')]
    urllib2.install_opener(opener)

    ptable=re.compile(r'<table class="yuBaoTable" .*?>(.*?)</table>',re.M|re.U|re.S)
    ptd=re.compile(r'<td.*?>(.*?)</td>',re.M|re.U|re.S)
    ptag=re.compile('(<.*?>)',re.M|re.U|re.S)
    try:
        res=opener.open(urllib2.Request(url))
    except urllib2.URLError:
        pass
    else:
        s=res.read()
        s=s.decode('utf8')
        all=[]
        
        tb=ptable.findall(s)[0]
        for td in ptd.findall(tb):
            content=ptag.sub(u'',td)
            content=content.strip(u'\r\n\t ')
            #print content
            content=content.replace(u'高温',u'最高气温')
            content=content.replace(u'低温',u'最高气温')
            content=content.replace(u'无持续风向',u'')
            if len(content)!=0:
                all.append(u'，')
                all.append(content)
            #print "\n"
        day_idx=all.index(u"白天")
        eve_idx=all.index(u"夜间")
        
        
        day=all[day_idx+2:eve_idx-1]
        eve=all[eve_idx+2:]
        
        if time == "day":
            msg = ''.join(day)
        elif time == "eve":
            msg = ''.join(eve)
        msg=msg.encode('utf8')

        return msg

if __name__=='__main__':
    msg = Weather('day')
    print "今天白天的天气是：%s" % msg

