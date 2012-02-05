# -*- coding: utf-8 -*-
## OAuth认证需要的 Consumer Key 和 Access Token

CONSUMER_KEY = 'MqOUJLBRkp9SYhG9dox1w'
CONSUMER_SECRET = 'Kf7dU6BFa4zw0g9kc5WeQOmLinLcsLTdApXRiGDEQ'
ACCESS_TOKEN = '258307067-ZGxSl0UMm1OAwqpYSWFvIsN1OpAQeDtFiHCPC4Rc'
ACCESS_SECRET = 'se9ztHd3GiuYm5bYXfVdeGQhUkiJ2MVHn7EryqXuE0'


#手动发Tweet的KEY
TWEET_KEY = 'V8Q6DvexTyCE3se47rtBX8em'
## 关键词
RT_REGEX="""diumoo|xdtuxbot|linux|unix|android|meego|ubuntu|arch|gentoo|debian|firefox|chrome|chromium|python| geek |apache|nginx|sql|php|django|rails|ruby|GPL|vim|emacs|gnome|gnu |perl|freebsd|netbsd|openbsd|hack|html5| kde """

MGC="gfw|翻墙|中共|土共|共产党|当局|政府|#notrt|#nort"

TALK="^@xdtuxbot"

## 访问路径
URL_RT = '/RT'                      # 推群
URL_TIMELINE = '/timeline'          # 时间线
URL_MENTIONS    = '/mentions'       # 提及页面
# 请修改此 CronJob Key 为其他人无法猜到的字符串，以防被人利用 (注意要和Cron.yaml中的保持同步)
KEY_CRONJOB     = '/CronJobXdTuxBot'
URL_SENDTWEET   = '/tweet'               # 手动发Tweet到Twitter (例如请求: /tweet2bot?msg='Hello World!')


## 个性化提示语设置
BOT_HASHTAG     = ' #xdlinux'                       # 特殊推中的HashTag
MSG_GET_UP      = ['早安世界，上午神马课阿',
                   '起床，学习去！',
                   '唔，昨晚梦见没纸了……',
                   '早安世界，好困哦！',
                   '早安世界，可是我还想睡！',
                   '早安世界，求调教！cc @htdong',
                   '早安世界，好想要 @mfs6174 来教我说话啊！',
                   '新的一天！伸个懒腰～ ʅ(‾◡◝)ʃ',
                   '一定要起床么，我还没睡醒唉…'
                    ]   # 早上 07:00 的起床推

MSG_SLEEP       = [ '主人，该睡觉了！要不我先去睡啦！晚安世界！',
                    '早起早睡身体好～ 喵呜～',
                    '晚安世界，晚安亲们 o(￣ε￣*) ',
                    '碎觉去，我想要个妹纸… 肿么了？机器人就不能喜欢妹纸么？ （＞﹏＜）　',
                    '做题做得好辛苦阿，不弄了，睡觉去!',
                    '碎觉碎觉，大家晚安！',
                    '晚安世界，晚安喵姑娘 @mfs6174'
                    ]# 晚上 23:55 的睡觉提醒 (例如：主人，该上床睡觉啦)

## 其他参数设置
MENTIONS_COUNT  = 15                              # 提及页面的显示条数
HOME_COUNT = 20                                   # 主页面显示条数

shorteners = ['t.co','tr.im','is.gd','tinyurl.com','bit.ly','snipurl.com','cli.gs',
                           'feedproxy.google.com','goo.gl','feeds.feedburner.com']

#天气参数 
CITY = "西安"
WOEID = "57036"
