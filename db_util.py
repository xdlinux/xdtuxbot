# DB function for zwbot
# -*- coding: utf-8 -*-

from google.appengine.ext import db

# DB计数器操作
class Counter(db.Model):
  count = db.IntegerProperty()
  is_title = db.IntegerProperty()
  current_title = db.StringProperty(multiline=False)
  current_word = db.StringProperty(multiline=False)
  rol_word1 = db.StringProperty(multiline=False)
  rol_word2 = db.StringProperty(multiline=False)
  rol_word3 = db.StringProperty(multiline=False)
  fatal_min = db.IntegerProperty()

class DB_Utility():
  def __init__(self):
    query = db.GqlQuery("select * from Counter")
    counter = query.get()
    
    if (not counter):
      counter = Counter()
      counter.count = 0
      counter.is_title = 0
      counter.current_title = ''
      counter.current_word = ''
      counter.rol_word1 = ''
      counter.rol_word2 = ''
      counter.rol_word3 = ''
      counter.fatal_min = -1
      counter.put()
  
  # max 是xls文件的最大行数，达到后从头开始
  def GetIncCounter(self, max):
    query = db.GqlQuery("select * from Counter")
    counter = query.get()
    
    result = counter.count                        # 取得当前的计数(从0开始)
    counter.count += 1
    counter.count = counter.count % max;          # 从 (0) - (max-1)
    
    counter.put()
    return(result)
  
  def GetCounter(self):
    q = db.GqlQuery("select * from Counter")
    counter = q.get()
    return(counter.count)
  
  def DecCounter(self):
    q = db.GqlQuery("select * from Counter")
    counter = q.get()
    if (counter.count > 0):
      counter.count -= 1
      counter.put()
  
  
  def GetTitleFlag(self):
    q = db.GqlQuery("select * from Counter")
    counter = q.get()
    return(counter.is_title)
  
  def SetTitleFlag(self, title, title_str):
    q = db.GqlQuery("select * from Counter")
    counter = q.get()
    counter.is_title = title
    if (title == 1):
      counter.current_title = title_str
    counter.put()
  
  def GetTitleString(self):
    q = db.GqlQuery("select * from Counter")
    counter = q.get()
    return(counter.current_title.encode('utf-8'))
  
  
  def GetCurrentWord(self):
    q = db.GqlQuery("select * from Counter")
    counter = q.get()
    return(counter.current_word.encode('utf-8'))
  
  def SetCurrentWord(self, str_word):
    q = db.GqlQuery("select * from Counter")
    counter = q.get()
    counter.current_word = str_word
    counter.put()
  
  def GetRollingWords(self):
    q = db.GqlQuery("select * from Counter")
    counter = q.get()
    str_word = '%s  %s  %s' % (counter.rol_word3, counter.rol_word2, counter.rol_word1)
    return(str_word.encode('utf-8'))
  
  def SetRollingWords(self, str_word):
    q = db.GqlQuery("select * from Counter")
    counter = q.get()
    counter.rol_word3 = counter.rol_word2
    counter.rol_word2 = counter.rol_word1
    counter.rol_word1 = str_word
    counter.put()
  
  
  # 读写推送失败的周期数
  def GetFatalMin(self):
    q = db.GqlQuery("select * from Counter")
    counter = q.get()
    return(counter.fatal_min)
  
  def SetFatalMin(self, iMin):
    q = db.GqlQuery("select * from Counter")
    counter = q.get()
    if (counter.fatal_min != iMin):
      counter.fatal_min = iMin
      counter.put()
