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

# When this is true, some things go to the screen as text and templates aren't always generated. Error message are more verbose.
_DEBUG = True

class SinceID(db.Model):
  since_id = db.IntegerProperty()


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
     
    max_id = self.request.get('max_id')  
    #logging.info(max_id)
   
    if max_id=='': 
        RT=api.list_timeline(owner='xdlinux',slug='rt-2',per_page=count+1,page=2)
        #RT = tweepy.Cursor(api.list_timeline,owner='xdlinux',slug='rt-2').items(count)
        max_id=RT[-1].id
        RT.pop()
    else:
        max_id=int(max_id)
        RT=api.list_timeline(owner='xdlinux',slug='rt-2',max_id=max_id,per_page=count+1)
        #RT = tweepy.Cursor(api.list_timeline,owner='xdlinux',slug='rt-2',max_id=max_id).items(count)
        max_id=RT[-1].id
        RT.pop()

    logging.info('Check list')
     
    next="RT?max_id=%d" % max_id
    
    path = os.path.join(os.path.dirname(__file__), 'template/index.html')
    self.response.out.write(template.render(path, { 'RT': RT ,'NEXT': next}))

# 自动回Fo所有新的Followers
class FollowAllNewcomers(webapp.RequestHandler):
  def get(self):
    auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
    auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_SECRET)
    api = tweepy.API(auth)
    
    followers_ids = tweepy.Cursor(api.followers_ids).items()
    followers_set = Set(followers_ids)
    friends_ids = tweepy.Cursor(api.friends_ids).items()
    friends_set = Set(friends_ids)
    
    suc_count = 0             # 成功建立关系的个数
    err_count = 0             # 可能已经发出申请的保护用户
    
    for user_id in (followers_set-friends_set):
      try:
        api.create_friendship(id=user_id)
        suc_count += 1
      except:
        err_count += 1
    
    logging.info('Follow %d user, skip %d.' % (suc_count, err_count))
    
    self.response.out.write('Success create_friendship() with %d user, %d skiped.' % (suc_count, err_count))

#
# Cron Job
#
class CronJobCheck(webapp.RequestHandler):
  def get(self):
    # r14 add @20101130 增加请求来源的判断，只接受由CronJob发起的请求
    Access_CronJob = False
    headers = self.request.headers.items()
    
    for key, value in headers:
      if (key == 'X-Appengine-Cron') and (value == 'true'):
        Access_CronJob = True
        break
    # 如果不是CronJob来源的请求，记录日志并放弃操作
    if (not Access_CronJob):
      logging.debug('CronJobCheck() access denied!')
      logging.critical('如果这个请求不是由你手动触发的话，这意味者你的CronJobKey已经泄漏！请立即修改CronJobKey以防被他人利用')
      return
    #
    
    mydate = datetime.utcnow() + timedelta(hours=+8)
    ts_hour = mydate.time().hour
    ts_min = mydate.time().minute
    
    if ((ts_hour == 7) and (ts_min == 0)):        # 7:00
        wther=weather.Weather('day')
        msg_idx=random.randint(0,len(config.MSG_GET_UP)-1)
        msg = '%s 今天西安的天气是:%s %s' % (config.MSG_GET_UP[msg_idx], wther, config.BOT_HASHTAG)
        resp=OAuth_UpdateTweet(msg)                        # 早安世界
    elif ((ts_hour == 23) and (ts_min == 30)):    # 23:30
        msg_idx=random.randint(0,len(config.MSG_SLEEP)-1)
        msg = '%s%s' % (config.MSG_SLEEP[msg_idx], config.BOT_HASHTAG)
        resp=OAuth_UpdateTweet(msg)                        # 晚安世界
       
    
    #wther=weather.Weather('day')
    #msg_idx=random.randint(0,len(config.MSG_GET_UP)-1)
    #msg = '%s 今天白天的天气是:%s %s' % (config.MSG_GET_UP[msg_idx], wther, config.BOT_HASHTAG)
    #logging.info(msg) 
    #return 
    auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
    auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_SECRET)
    api = tweepy.API(auth)
    
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
    tweets=timeline[::-1]   # 时间是倒序的
    if tweets == []:
        logging.info("no new tweets!")
        return
    for tweet in tweets:
        user = tweet.user.screen_name
        if user == 'xdtuxbot':
            continue
        text = tweet.text

        m = regx.match(text)
        if m == None:
            continue

        msg = 'RT @%s:%s' % (user,text)
        #logging.info(msg)
        
        #self.response.out.write('Sending message %s<br />' % msg)
        try:
          resp=OAuth_UpdateTweet(msg)                        # 发送到Twitter
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
