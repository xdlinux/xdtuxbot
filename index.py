# zwbot project on GAE
# -*- coding: utf-8 -*-
import os
import logging
import re
from sets import Set
from datetime import datetime, timedelta
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from google.appengine.ext import db
import random
import weather
import config 
import tweepy
import urlparse,httplib
import command

# When this is true, some things go to the screen as text and templates aren't always generated. Error message are more verbose.
_DEBUG = True

class SinceID(db.Model):
  since_id = db.IntegerProperty()

# 展开t.co网址
def url_expand( url ):
    components = urlparse.urlparse(url)
    c = httplib.HTTPConnection(components.netloc)
    c.request("GET",components.path)
    r = c.getresponse()
    l = r.getheader('Location')
    if l == None:
        return url
    else:
        hl = urlparse.urlparse(l).netloc
        if hl in config.shorteners:
            return url_expand( l )
        else:
            return l

def parse_content( content ):
    
    # 处理@
    content = re.sub(r'@(.*?)(\s|:|$)',
                     r'<a href="https://twitter.com/\1">@\1</a>\2',
                    content)
    # 处理#
    content = re.sub(r'#(.*?)(\s|$)',
            r'<a href="https://twitter.com/search/%23\1">#\1</a>\2',
                    content)
   
    # 展开网址
    
    content = re.sub(r'(http://.*?)(\s|$)',
                     r'<a href="\1">\1</a>\2',
                     content)

    r_url = re.compile('<a.*>(http://t.co/.*?)</a>')
    m = r_url.findall(content)
    for s_url in m:
        print s_url
        if s_url != '':
            l_url = url_expand( s_url )
            print l_url
            content += '<div class="long-url"><a href="%s">%s</a></div>' \
                % ( l_url, l_url)
    
    content = re.sub(r'\n','<br>',content)
    return content

# OAuth认证并发推
def OAuth_UpdateTweet(msg):
  if msg != '':
    auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
    auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_SECRET)
    api = tweepy.API(auth)
    return(api.update_status(msg))

# 请求 /
class MainPage(webapp.RequestHandler):
  def get(self):
    msg = 'It work!'
    path = os.path.join(os.path.dirname(__file__), 'template/msg.html')
    self.response.out.write(template.render(path, { 'msg': msg }))

# [ADMIN] 请求提及页面，显示最近的15条@消息
class GetMentions(webapp.RequestHandler):
  def get(self):
    auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
    auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_SECRET)
    api = tweepy.API(auth)
    mentions = tweepy.Cursor(api.mentions).items(config.MENTIONS_COUNT)
    
    logging.info('Check Mentions')
    
    path = os.path.join(os.path.dirname(__file__), 'template/mentions.html')
    self.response.out.write(template.render(path, { 'mentions': mentions }))

# TimeLine
class GetTimeline(webapp.RequestHandler):
  def get(self):
    auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
    auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_SECRET)
    api = tweepy.API(auth)
    timeline = tweepy.Cursor(api.home_timeline).items(config.HOME_COUNT)
    
    logging.info('Check Timeline')
    
    path = os.path.join(os.path.dirname(__file__), 'template/timeline.html')
    self.response.out.write(template.render(path, { 'timeline': timeline }))

# RT list
class GetList(webapp.RequestHandler):
  def get(self):
    count=config.HOME_COUNT
    auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
    auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_SECRET)
    api = tweepy.API(auth)
    
    user = self.request.get('user')
    if user == 'xdlinux':
        slug = 'rt-2'
    elif user == 'xdlinuxbot':
        slug = 'rt'
    else:
        user = 'xdlinux'
        slug = 'rt-2'
    page = self.request.get('page')
    if page == '':
        page = 1
    else:
        page = int(page)

    RT=api.list_timeline(owner=user,slug=slug,per_page=count,page=page)

    logging.info('Check list')
    logging.info(RT[0].created_at)
    
    #时区调整
    for i in range(len(RT)):
        Ttime=str(RT[i].created_at)
        Ttime=Ttime.replace(':','-')
        Ttime=Ttime.replace(' ','-')
        T=Ttime.split('-')
        for t in range(6): 
            T[t]=int(T[t])
        Ttime=datetime(T[0],T[1],T[2],T[3],T[4],T[5])+timedelta(hours=+8)
        RT[i].created_at=Ttime.strftime('%Y-%m-%d %H:%M:%S')
    #超链接和@ 
    for i in range(len(RT)):
        content = RT[i].text
        content = parse_content( content )
        RT[i].text = content
        #logging.info(content)

    next="RT?user=%s&page=%d" % (user,(page+1))
    if page > 1:
        prev="RT?user=%s&page=%d" % (user,(page-1))
    else:
        prev=''
    
    path = os.path.join(os.path.dirname(__file__), 'template/index.html')
    self.response.out.write(template.render(path, { 'RT': RT ,'NEXT': next, 'PREV':prev, 'LIST':user}))
# Cron Job
class CronJobCheck(webapp.RequestHandler):
  def get(self):
    Access_CronJob = True
    headers = self.request.headers.items()
     
    for key, value in headers:
      if (key == 'X-Appengine-Cron') and (value == 'true'):
        Access_CronJob = True
        break
    # 如果不是CronJob来源的请求，记录日志并放弃操作
    if (not Access_CronJob):
      logging.debug('CronJobCheck() access denied!')
      logging.critical('如果这个请求不是由你手动触发的话，这意味者你的CronJobKey已经泄漏！请立即修改CronJobKey以防被他人利用')
    #  return
    
    mydate = datetime.utcnow() + timedelta(hours=+8)
    ts_hour = mydate.time().hour
    ts_min = mydate.time().minute
    
    dbug = self.request.get('debug')
    logging.debug(dbug)


    # 7:00早安世界
    if (((ts_hour == 7) and ( 0 <= ts_min <= 2)) or (dbug=='morning')): # 7:00
        error = False
        try:
            wther=weather.weather()
        except weather.FetchError:
            logging.error("Weather Fetch Error!")
            error = True
        msg_idx=random.randint(0,len(config.MSG_GET_UP)-1)
        if error:
            msg = '%s%s' % (config.MSG_GET_UP[msg_idx],config.BOT_HASHTAG)
        else:
            msg = '%s 今天西安的天气是:%s %s' % \
                (config.MSG_GET_UP[msg_idx], wther[0], config.BOT_HASHTAG)
        
        resp=OAuth_UpdateTweet(msg)                        # 早安世界
        logging.info("%s:%d" % (msg,wther[1]))
   
    # 23:30 晚安世界
    elif ((ts_hour == 23) and (30 <= ts_min <=32)):    # 23:30
        msg_idx=random.randint(0,len(config.MSG_SLEEP)-1)
        msg = '%s%s' % (config.MSG_SLEEP[msg_idx], config.BOT_HASHTAG)
        resp=OAuth_UpdateTweet(msg)                        # 晚安世界
        logging.info(msg)
  
    # 每小时一条命令
    elif (((7<=ts_hour<=23) and (15<=ts_min<=17)) or (dbug=='cli')):
        msg = command.random()
        if msg != None:
            msg = msg.replace("# commandlinefu.com by David Winterbottom\n\n#","//")
            msg = '%s %s' % ( "叮咚！小bot教CLI时间到了！", msg[:-1])
            msg +="#commandlinefu"
            logging.info(msg)
            resp = OAuth_UpdateTweet(msg)

    # 扫TL，转推
    auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
    auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_SECRET)
    api = tweepy.API(auth)
    
    #since id
    tweetid=SinceID.all().get()
    logging.info(tweetid)
    if ( tweetid == None ):
        logging.warning("Initial!")
        tweetid=SinceID()
        timeline = api.home_timeline()
    else:
        logging.info("Since ID is: %d" % tweetid.since_id)
        timeline = api.home_timeline(since_id=tweetid.since_id)
    
    #self.response.out.write('GETTING TIMELINE<br />')
    regx=re.compile(config.RT_REGEX,re.I|re.M)
    mgc = re.compile(config.MGC,re.I|re.M)
    tweets=timeline[::-1]   # 时间是倒序的
    if tweets == []:
        logging.info("no new tweets!")
        return
    
    for tweet in tweets:
        user = tweet.user.screen_name
        if user == 'xdtuxbot':
            continue
        
        text = tweet.text
        m = regx.search(text)
        if m == None:
            continue
        n = mgc.search(text)
        if n != None:
            continue


        msg = 'RT @%s:%s' % (user,text)
        #logging.info(msg)
        
        try:
          resp=OAuth_UpdateTweet(msg)           # 发送到Twitter
          logging.info('Send Tweet: %s, rtn %s' % (msg, resp))
        except tweepy.TweepError, e:
            msg = 'Tweepy Error:%s' % e
            logging.error(msg)
        except Exception, e:
            msg = 'Uknow Error'
            logging.error(msg)
    
    tweetid.since_id=tweet.id
    logging.info("Next Since ID: %d" % tweetid.since_id)
    tweetid.put()

    path = os.path.join(os.path.dirname(__file__), 'template/timeline.html')
    self.response.out.write(template.render(path, { 'timeline': timeline }))



# 发送独立的 msg 到Twitter
class SendTweet2Twitter(webapp.RequestHandler):
  def get(self):
    msg = self.request.get('msg')
    try:
      if msg != '':
        resp = OAuth_UpdateTweet(msg)
        
        logging.info('Send Tweet: %s, rtn %s' % (msg, resp))
        
        out_text = 'Send Tweet: %s' % msg
        path = os.path.join(os.path.dirname(__file__), 'template/msg.html')
        self.response.out.write(template.render(path, { 'msg': out_text }))
        
      else:
        self.response.out.write('Invalid Input.')
      
    except (TypeError, ValueError):
      self.response.out.write('Invalid Input!')



application = webapp.WSGIApplication([('/',GetList),
                                      (config.URL_RT, GetList),
                                      (config.URL_TIMELINE,GetTimeline),
                                      (config.URL_MENTIONS, GetMentions),
                                      (config.KEY_CRONJOB, CronJobCheck),
                                     ], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
