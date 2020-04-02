# -*- coding: utf-8 -*-

"""
File Name：          config
Description :
Author :             gregory
Date：               2018/5/9:下午9:27
Change Activity:     2018/5/9:下午9:27

"""

from common.base.logger import *

# 启动配置
DEBUG = True
FHOST = '0.0.0.0'
FPORT = 8002

# 日志配置
install('logs/multi-sender.log')
# install('stdout')
log = logging.getLogger()

# 邮件配置
smtp_server = 'smtp.exmail.qq.com'
mailname = 'alert@xxkeji.com'
mailpass = 'xxxxxx'

# 短信配置
smsapi = 'http://xx.com/sender'
smsid = '12345678'
smsname = 'xxxxxx'
smspass = 'xxxxxx'
smsprefix = '【xx】' # 短信通道需要标签才能发出
smspridid = 'xxxxxx'
