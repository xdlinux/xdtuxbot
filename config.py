# zwbot configure
# -*- coding: utf-8 -*-

##
## 部署到GAE前，请参照 DeploymentGuide 修改下列配置，并且自定义你的bot
##  http://code.google.com/p/zwbot/wiki/DeploymentGuide
##

## OAuth认证需要的 Consumer Key 和 Access Token
## August 31, 2010, Basic Auth has been deprecated. All applications must now use OAuth
CONSUMER_KEY = 'NxRNiatciHHyyIjOajlo6g'
CONSUMER_SECRET = 'U9mQR5s1TixeWkjQxNunGIK72ynLb0bllKjWVFQXU2w'
ACCESS_TOKEN = '246485694-XHWHlIAWSpIJWSm1y1HVfU5EeKnQA4Xn9Jcrm39S'
ACCESS_SECRET = 'hJ0aGfaZAlolBOYbjh9j5DcjaMOZsFOrPnsYDg32t4'


## 词库配置
DICT_NAME       = 'static/sample_dict.xls'        # 词库名，注意是绝对路径
DICT_LINES      = 24                              # 词库中记录条数 (达到此条数会自动从头开始播放)


## 访问路径
URL_CURWORD     = '/t'                            # 当前单词页面
URL_MENTIONS    = '/backdoor2checkmentions'       # 提及页面
KEY_FOBACK_ALL  = '/AutoFollowBack'               # 回Fo动作的触发名 (注意要和Cron.yaml中的保持同步)
# 请修改此 CronJob Key 为其他人无法猜到的字符串，以防被人利用 (注意要和Cron.yaml中的保持同步)
KEY_CRONJOB     = '/InputYourCronJobKeyHere'
URL_SENDTWEET   = '/backdoor2tweet'               # 手动发Tweet到Twitter (例如请求: /tweet2bot?msg='Hello World!')


## 个性化提示语设置
BOT_HASHTAG     = ' #zwbot'                       # 特殊推中的HashTag，用于复习索引 (不需要请留空)
MSG_GET_UP      = '现在是bot的起床时间'           # 早上 07:00 的起床提醒 (例如：主人，该起床背单词了哦)
MSG_SLEEP       = '现在是bot的休息时间'           # 晚上 23:55 的睡觉提醒 (例如：主人，该上床睡觉啦)

# 复习推前后的提示语，构成 {MSG_REVIEW_1 + 三个单词 + MSG_REVIEW_2} 的格式
MSG_REVIEW_1    = '复习时间 '
MSG_REVIEW_2    = ' 还记得这三个单词的意思吗？'
# 深夜访问GAE的 /t 页面显示的提示
GAE_PAGE_TIPS   = '现在是bot的休息时间'

## 其他参数设置
MENTIONS_COUNT  = 15                              # 提及页面的显示条数

# 单词的连接符和分隔符
TW_WORD_LINK    = ' - '                           # 单元格A和单元格B之间的连接符
TW_WORD_SP      = '; '                            # 单元格B和单元格C之间的分隔符
