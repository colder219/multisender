# -*- coding: utf-8 -*-

"""
File Name：          sendtools.py
Description :
Author :             gregory
Date：               2018/5/10:下午4:10
Change Activity:     2018/5/10:下午4:10

"""

from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr
import smtplib
import urllib.error
import xml.dom.minidom
import urllib.request
from config import log
import config
import requests
import json


class MailHandler():
    def _format_addr(self, s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def sendmail(self, to_list, subject, content):
        from_addr = config.mailname
        mailPass = config.mailpass
        smtp_server = config.smtp_server

        msg = MIMEText(content, 'html', 'utf-8')
        msg['From'] = self._format_addr('Alert <%s>' % from_addr)
        msg['Subject'] = Header(subject, 'utf-8')

        # 这一块可以不要，我们这边P5、P6页面看看就行
        if "P5" in content or "P6" in content:
            log.info("P5、P6级别的报警不发送邮件")
            print("P5、P6级别的报警不发送邮件")
        else:
            # 发送邮件
            log.info("发送邮件给: %s" % to_list)
            log.info("邮件内容：%s" % content)
            try:
                server = smtplib.SMTP()
                server.connect(smtp_server)
                server.login(from_addr, mailPass)
                server.sendmail(from_addr, to_list, msg.as_string())
                server.quit()
                print('发送成功')
            except Exception as e:
                print("邮件发送失败")
                str(e)


class SmsHandler():
    def sendsms(self, to_list, content):
        log.info("发送短信给: %s" % to_list)
        log.info("短信内容：%s" % content)
        for i in range(len(to_list)):
            sname = config.smsname
            spwd = config.smspass
            sprdid = config.smsid
            param = {'sname': '%s' % sname,  # 账号
                     'spwd': '%s' % spwd,  # 密码
                     'scorpid': '',  # 企业代码
                     'sprdid': '%s' % sprdid,  # 产品编号
                     'sdst': '%s' % to_list[i],  # 手机号码
                     'smsg': '%s' % content}  # 短信内容
            data = urllib.parse.urlencode(param).encode(encoding='UTF8')
            # 定义头
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            # 开始提交数据
            req = urllib.request.Request(config.smsapi, data, headers)
            response = urllib.request.urlopen(req)
            # 获取返回数据
            result = response.read().decode('utf8')
            # 自行解析返回结果xml，对应结果参考文档
            dom = xml.dom.minidom.parseString(result)
            root = dom.documentElement
            State = root.getElementsByTagName("State")
            MsgID = root.getElementsByTagName("MsgID")
            MsgState = root.getElementsByTagName("MsgState")
            Reserve = root.getElementsByTagName("Reserve")
            print(State[0].firstChild.data)  # State值为0表示提交成功
            print(MsgID[0].firstChild.data)
            print(MsgState[0].firstChild.data)
            print(Reserve[0].firstChild.data)


class TelHandler():
    def sendtel(self, to_list):
        url = "http://cf.51welink.com/submitdata/Service.asmx/g_Submit"
        log.info("发送短信给: %s" % to_list)
        for i in range(len(to_list)):
            sname = config.smsname
            spwd = config.smspass
            sprdid = config.smsid  # 没有的可以忽略这个
            content = '001110'  # 电话代号，只提供叫醒
            param = {'sname': '%s' % sname,  # 账号
                     'spwd': '%s' % spwd,  # 密码
                     'scorpid': '',  # 企业代码
                     'sprdid': '%s' % sprdid,  # 产品编号
                     'sdst': '%s' % to_list[i],  # 手机号码
                     'smsg': '%s' % content}  # 短信内容
            data = urllib.parse.urlencode(param).encode(encoding='UTF8')
            # 定义头
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            # 开始提交数据
            req = urllib.request.Request(url, data, headers)
            response = urllib.request.urlopen(req)
            # 获取返回数据
            result = response.read().decode('utf8')
            # 自行解析返回结果xml，对应结果参考文档
            dom = xml.dom.minidom.parseString(result)
            root = dom.documentElement
            State = root.getElementsByTagName("State")
            MsgID = root.getElementsByTagName("MsgID")
            MsgState = root.getElementsByTagName("MsgState")
            Reserve = root.getElementsByTagName("Reserve")
            print(State[0].firstChild.data)  # State值为0表示提交成功
            print(MsgID[0].firstChild.data)
            print(MsgState[0].firstChild.data)
            print(Reserve[0].firstChild.data)


class GrafanaSmsHandler():

    # def sendsms(self):
    def sendsms(self, to_list, content):
        log.info("发送短信给: %s" % to_list)
        log.info("短信内容：%s" % content)
        for i in range(len(to_list)):
            sname = config.smsname
            spwd = config.smspass
            sprdid = config.smsid  # 没有的可以忽略这个
            param = {'sname': '%s' % sname,  # 账号
                     'spwd': '%s' % spwd,  # 密码
                     'scorpid': '',  # 企业代码
                     'sprdid': '%s' % sprdid,  # 产品编号
                     'sdst': '%s' % to_list[i],  # 手机号码
                     'smsg': '%s' % content}  # 短信内容
            data = urllib.parse.urlencode(param).encode(encoding='UTF8')
            # 定义头
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            # 开始提交数据
            req = urllib.request.Request(config.smsapi, data, headers)
            response = urllib.request.urlopen(req)
            # 获取返回数据
            result = response.read().decode('utf8')
            # 自行解析返回结果xml，对应结果参考文档
            dom = xml.dom.minidom.parseString(result)
            root = dom.documentElement
            State = root.getElementsByTagName("State")
            MsgID = root.getElementsByTagName("MsgID")
            MsgState = root.getElementsByTagName("MsgState")
            Reserve = root.getElementsByTagName("Reserve")
            print(State[0].firstChild.data)  # State值为0表示提交成功
            print(MsgID[0].firstChild.data)
            print(MsgState[0].firstChild.data)
            print(Reserve[0].firstChild.data)


class GrafanaSmsHandler():

    # def sendsms(self):
    def sendsms(self, to_list, content):
        url = "http://cf.51welink.com/submitdata/Service.asmx/g_Submit"
        log.info("发送短信给: %s" % to_list)
        log.info("短信内容：%s" % content)
        for i in range(len(to_list)):
            sname = 'dlxiaoch'
            spwd = 'oN7GPX6k'
            sprdid = '1012818'
            param = {'sname': '%s' % sname,  # 账号
                     'spwd': '%s' % spwd,  # 密码
                     'scorpid': '',  # 企业代码
                     'sprdid': '%s' % sprdid,  # 产品编号
                     'sdst': '%s' % to_list[i],  # 手机号码
                     'smsg': '%s' % content}  # 短信内容
            data = urllib.parse.urlencode(param).encode(encoding='UTF8')
            # 定义头
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            # 开始提交数据
            req = urllib.request.Request(url, data, headers)
            response = urllib.request.urlopen(req)
            # 获取返回数据
            result = response.read().decode('utf8')
            # 自行解析返回结果xml，对应结果参考文档
            dom = xml.dom.minidom.parseString(result)
            root = dom.documentElement
            State = root.getElementsByTagName("State")
            MsgID = root.getElementsByTagName("MsgID")
            MsgState = root.getElementsByTagName("MsgState")
            Reserve = root.getElementsByTagName("Reserve")
            print(State[0].firstChild.data)  # State值为0表示提交成功
            print(MsgID[0].firstChild.data)
            print(MsgState[0].firstChild.data)
            print(Reserve[0].firstChild.data)


class DingDingHandler():
    @staticmethod
    def http_post(webhook, data):
        headers = {"Content-Type": "application/json"}
        data = json.dumps(data)
        try:
            response = requests.post(webhook, data=data, headers=headers)
        except Exception as e:
            return None

        code = response.status_code
        if code != 200:
            return None

        resp = response.json()
        return resp


if __name__ == '__main__':
    g = TelHandler()
    g.sendtel(['18888888888', '1999999999'])
