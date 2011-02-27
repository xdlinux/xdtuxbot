# zwbot project on GAE
# -*- coding: utf-8 -*-
import os
import sys
import base64
import urllib
import csv
import logging
import string
from sets import Set
from datetime import datetime, timedelta
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

import config       # r14 add @20101215 独立bot的配置文件
import db_util      # r2 add  @20101026 将数据库相关操作独立出来

#sys.path.insert(0, 'tweepy.zip')
import tweepy

# r2 add @20101026 替换csv为xls文件，加速读取
sys.path.insert(0, 'xlrd-0.6.1.zip')
import xlrd

# When this is true, some things go to the screen as text and templates aren't always generated. Error message are more verbose.
_DEBUG = True


# OAuth认证并发推
def OAuth_UpdateTweet(msg):
  if msg != '':
    auth = tweepy.OAuthHandler(config.CONSUMER_KEY, config.CONSUMER_SECRET)
    auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_SECRET)
    api = tweepy.API(auth)
    return(api.update_status(msg))


# 读取词典文件中的下一个单词
def GetNextTweetword_from_Dict():
  udb = db_util.DB_Utility()
  
  index = udb.GetIncCounter(config.DICT_LINES)
  xlswb = xlrd.open_workbook(config.DICT_NAME)
  
  sheet1 = xlswb.sheet_by_index(0)
  title_line = 0
  
  try:
    if (sheet1.cell_value(index, 0) == ''):
      str = sheet1.cell_value(index, 1)
      title_line = 1
    else:
      str = '%s%s%s' % ( sheet1.cell_value(index, 0), config.TW_WORD_LINK, sheet1.cell_value(index, 1) )
    
    if (len(sheet1.row_values(index)) > 2):     # 如果有第三列，取出来附加上
      if (sheet1.cell_value(index, 2) != ''):
        str = '%s%s%s' % ( str, config.TW_WORD_SP, sheet1.cell_value(index, 2) )
    
    tweet = str
    udb.SetTitleFlag(title_line, tweet)
    
    if title_line == 0:
      ssp = sheet1.cell_value(index, 0).split()
      udb.SetRollingWords(ssp[0])                 # 取出开始的单词，用于复习
      udb.SetCurrentWord(tweet)
    else:
      tweet = '%s%s' % (tweet, config.BOT_HASHTAG)
    
  except:
    tweet = ''
  
  return(tweet)


# 请求 /
class MainPage(webapp.RequestHandler):
  def get(self):
    msg = 'It work!'
    path = os.path.join(os.path.dirname(__file__), 'template/msg.html')
    self.response.out.write(template.render(path, { 'msg': msg }))

# 请求 /t
class ShowCurrentWord(webapp.RequestHandler):
  def get(self):
    mydate = datetime.utcnow() + timedelta(hours=+8)
    ts_hour = mydate.time().hour
    ts_min = mydate.time().minute / 5
    
    udb = db_util.DB_Utility()
    
    if (ts_hour < 7):
      words = '%s' % config.GAE_PAGE_TIPS
    else:
      words = '%s<BR>%s' % ( udb.GetTitleString(), udb.GetCurrentWord() )
      logging.debug('ShowCurrentWord(): "%s"' % words)
    
    path = os.path.join(os.path.dirname(__file__), 'template/words.html')
    self.response.out.write(template.render(path, { 'words': words }))

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
        RT=api.list_timeline(owner='xdlinux',slug='rt-2',per_page=count+1)
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
    
    mydate = datetime.utcnow() + timedelta(hours=+8)
    ts_hour = mydate.time().hour
    ts_min = mydate.time().minute / 5
    
    udb = db_util.DB_Utility()
    
    # 7:00 ~ 23:59 是工作时间，不满足工作时间的直接返回
    if (ts_hour < 7):
      return
    
    # 检查之前是否有失败发生
    if (not ts_min in [0, 3, 6, 9, 11]):          # 分钟为 00/15/30/45/55 的周期才继续处理
      if (udb.GetFatalMin() != -1):               # 或者上次有失败发生，重设周期数继续
        ts_min = udb.GetFatalMin()
        if (udb.GetTitleFlag() == 0):
          logging.warning('上次失败发生在 %d 分，尝试进行恢复...' % (ts_min*5))
          if (ts_min in [0, 3, 6]):
            udb.DecCounter()                      # 退回到上一次的count处
      else:                                       # 没有失败，直接返回
        return
    
    if ((ts_hour == 7) and (ts_min == 0)):        # 7:00
      msg = '%s%s' % (config.MSG_GET_UP, config.BOT_HASHTAG)
    elif ((ts_hour == 23) and (ts_min == 11)):    # 23:55
      msg = '%s%s' % (config.MSG_SLEEP, config.BOT_HASHTAG)
    elif (ts_min in [0, 3, 6]):                   # every 00/15/30 推单词
      msg = GetNextTweetword_from_Dict()
    elif (ts_min == 9):                           # every 45 (复习)
      msg = '%s%s%s%s' % (config.MSG_REVIEW_1, udb.GetRollingWords(), config.MSG_REVIEW_2, config.BOT_HASHTAG)
    else:                                         # every 55 (不是23:55，不处理)
      return
    
    logging.info('Send Tweet: %s' % msg)
    
    try:
      OAuth_UpdateTweet(msg)                        # 发送到Twitter
      udb.SetFatalMin(-1)                           # 如果执行成功，将失败周期数改回-1
      
      # 检查刚才发送的是否为标题，如果是则设置失败min，让下个5分钟继续推一条
      if (udb.GetTitleFlag() == 1):
        udb.SetFatalMin(ts_min)
      
      #logging.debug('Auto tweet success complete.')
    except tweepy.TweepError, e:
      if ('Status is a duplicate' in e):            # 说明Tweet已经发出去了，清除掉这个失败
        udb.SetFatalMin(-1)
        msg = '[WARN] 尝试恢复 %d 时刻的Tweet，但该Tweet已存在: %s' % (ts_min*5, e)
        logging.warring(msg)
      else:
        udb.SetFatalMin(ts_min)
        msg = '[Tweepy错误] 错误发生在 %d 分, %s' % (ts_min*5, e)
        logging.error(msg)
    except Exception, e:
      msg = '[未知错误] 错误发生在 %d 分, %s' % (ts_min*5, e)
      logging.error(msg)
    
    path = os.path.join(os.path.dirname(__file__), 'template/msg.html')
    self.response.out.write(template.render(path, { 'msg': msg }))

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
                                      ('/RT', GetList),
                                      ('/timeline',GetTimeline),
                                      (config.URL_MENTIONS, GetMentions),
                                      (config.KEY_FOBACK_ALL, FollowAllNewcomers),
                                      (config.KEY_CRONJOB, CronJobCheck),
                                      (config.URL_SENDTWEET, SendTweet2Twitter)
                                     ], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
