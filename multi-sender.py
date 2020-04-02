# coding:utf-8
# Author: sunhong
# Created Time : 五  2/23 23:53:01 2018
# File Name: multi-sender.py

from flask import Flask, request
from flask_restful import Api, Resource, reqparse, request
import config
from sendtools import *
from config import *
import json
import datetime

app = Flask(__name__)
api = Api(app)
app.config.from_object(config)


class mailApi(Resource):
    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument("tos", type=str, help="收件人列表")
        parse.add_argument("subject", type=str, help="邮件主题")
        parse.add_argument("content", type=str, help="邮件内容")

        args = parse.parse_args()
        mailhand = MailHandler()
        to_list = args.tos.split(',')
        mailhand.sendmail(to_list, args.subject, args.content)
        return args


class falconDingDingApi(Resource):
    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument("tos", type=str, help="webhook")
        # parse.add_argument("subject", type=str, help="钉钉主题")
        parse.add_argument('content', type=str, help='报警内容')

        args = parse.parse_args()
        webhook = args.tos
        content = args.content
        tilte = "dingding alert"

        content = {'msgtype': 'markdown', 'markdown': {'title': tilte, 'text': content}}

        resp = DingDingHandler.http_post(webhook, content)
        return resp


class dingDingApi(Resource):
    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument('webhook', type=str, help='钉钉报警链接')
        parse.add_argument('content', type=str, help='报警内容')
        parse.add_argument('title', type=str, help='标题')
        parse.add_argument('contact', type=str, help='联系人')

        args = parse.parse_args()
        webhook = args.webhook
        content = args.content
        tilte = args.title
        contact = args.contact
        if contact is not None:
            contacts = contact.split(',')
            atcontent = "@" + "@".join(contacts)
            print('latcontent:{}'.format(atcontent))
            content = '{}\n\n'.format(atcontent) + '**报警标题:{}**\n\n'.format(tilte) + content
        else:
            contacts = None

        print('contacts:{}'.format(contacts))

        content = {'msgtype': 'markdown', 'markdown': {'title': tilte, 'text': content},
                   'at': {'atMobiles': contacts}}

        resp = DingDingHandler.http_post(webhook, content)
        return resp


class smsApi(Resource):
    def insert_dash(self, string, index):
        return string[:index] + '\n' + string[index:]

    def delete_dash(self, string, index, lenx):
        return string[:index] + string[index + lenx:]

    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument("tos", type=str, help="收件人列表")
        parse.add_argument("content", type=str, help="短信内容")

        args = parse.parse_args()
        con = args.content

        aum = con.count('[]')
        log.info("有 %d 个 空 [],将会被删除" % aum)
        e = 0

        for i in range(aum):
            x = con.find('[]', e)
            con = self.delete_dash(con, x, len('[]'))
            e = x

        num = con.count(']')
        log.info("有 %d 个地方需要换行" % num)
        f = 0
        for i in range(num):
            b = con.find(']', f) + 1
            con = self.insert_dash(con, b)
            f = b

        # 短信删除报警级别，方便在短信列表预览
        del_s = con.find('[P')
        del_e = con.find('\n', del_s)
        con = con[del_e + 1:]

        log.info('content: %s' % con)
        content_prefix = config.smsprefix + ' \n'
        content = content_prefix + con
        args = parse.parse_args()
        smshand = SmsHandler()
        to_list = args.tos.split(',')
        print(to_list)

        smshand.sendsms(to_list, content)
        return args


class GrafanaSmsApi(Resource):
    def post(self):
        parse = reqparse.RequestParser()
        # parse.add_argument("mobile", type=str, help="收件人列表")
        parse.add_argument("state", type=str, help="状态")
        parse.add_argument("ruleName", type=str, help="规则名称")
        parse.add_argument("message", type=str, help="信息")
        parse.add_argument("evalMatches", type=str, help="metic")

        args = parse.parse_args()
        state = args.state
        rulename = args.ruleName
        metic = args.evalMatches
        message = args.message
        con = "报警状态:" + args.state + "\n规则名称:" + args.ruleName + "\n"
        if metic is not None:
            con = con + "详细信息:" + args.evalMatches

        log.info('content: %s' % con)
        content_prefix = config.smsprefix + ' \n'
        content = content_prefix + con
        smshand = SmsHandler()
        to_list = message.split(',')
        print(to_list)

        smshand.sendsms(to_list, content)
        return args


class GrafanaTelApi(Resource):
    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument("message", type=str, help="信息")
        args = parse.parse_args()
        message = args.message
        to_list = message.split(',')

        telhand = TelHandler()
        telhand.sendtel(to_list)
        return args


class GrafanaDingDingApi(Resource):
    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument("state", type=str, help="状态")
        parse.add_argument("ruleName", type=str, help="规则名称")
        parse.add_argument("message", type=str, help="webhook")
        parse.add_argument("evalMatches", type=str, help="metic")

        args = parse.parse_args()
        state = args.state
        rulename = args.ruleName
        metic = args.evalMatches
        con = "** 报警状态:" + state + "** \n\n **规则名称:" + rulename + "** \n\n"
        if metic is not None:
            con = con + "详细信息:\n\n"
            con = con + "> " + args.evalMatches
        content = {'msgtype': 'markdown', 'markdown': {'title': '生产报警', 'text': con}}
        webhook = args.message
        print(webhook)

        DingDingHandler.http_post(webhook, content)
        return args


class GrafanaMailApi(Resource):
    def post(self):
        parse = reqparse.RequestParser()
        parse.add_argument("state", type=str, help="状态")
        parse.add_argument("ruleName", type=str, help="规则名称")
        parse.add_argument("message", type=str, help="webhook")
        parse.add_argument("evalMatches", type=str, help="metic")

        args = parse.parse_args()
        state = args.state
        rulename = args.ruleName
        metic = args.evalMatches
        con = "** 报警状态:" + state + "** \n\n **规则名称:" + rulename + "** \n\n"
        if metic is not None:
            con = con + "详细信息:\n\n"
            con = con + args.evalMatches
        content = con
        webhook = args.message
        print(webhook)

        mailhand = MailHandler()
        mailhand.sendmail(webhook, rulename, content)
        return args


class AlertManagerApi(Resource):
    def post(self):
        requestbody = request.get_data()
        requestbody = json.loads(requestbody)
        thistime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%d")

        print(requestbody)
        # 这个字典存的项目和负责人的关系
        contact_list = {'media': ['1888888888', 'zhangsan'], 'login': ['1999999999', 'lisi']}
        alerts = requestbody.get('alerts')
        webhook = 'https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxx'
        silence_url = 'http://alertmanager.xxkeji.com/#/alerts'
        for i in alerts:
            level = i.get('labels').get('severity')
            starttime = i.get('startsAt')
            status = i.get('status')
            job = i.get('labels').get('service')
            print('service:{}'.format(job))
            try:
                contact = contact_list.get(job)[0]
            except Exception as e:
                contact = '18888888888'
            print(contact)
            annotions = i.get('annotations').get('summay')
            description = i.get('annotations').get('description')

            description = description.replace('(', '%28')
            description = description.replace(')', '%29')
            description = '[grafana]' + '({})'.format(description)
            print(description)
            generatorURL = i.get('generatorURL')
            generatorURL = generatorURL.replace('tab=0', 'tab=1')
            generatorURL = '[prometheus]' + '({})'.format(generatorURL)
            # 因域名没有解析，这里转换为ip，方便设置静默使用
            if 'monitor01' in generatorURL:
                generatorURL = generatorURL.replace('shal-xx-xx-xx01.in.xxkeji.com', '192.168.0.1')
            elif 'monitor03' in generatorURL:
                generatorURL = generatorURL.replace('shal-xx-xx-xx02.in.xxkeji.com', '192.168.0.2')

            alert_url = description + ',' + generatorURL

            # if status == 'firing':
            alertinf = "@{}\n\n**报警级别:**{}\n\n**报警时间:**{}\n\n**报警信息:**{}\n\n **监控信息:**{}\n\n **设置静默:**{}".format(
                contact,
                level, starttime, annotions, alert_url,
                silence_url)
            contacts = [contact]
            content = {'msgtype': 'markdown', 'markdown': {'title': '生产报警', 'text': alertinf},
                       'at': {'atMobiles': '{}'.format(contacts)}}
            print('thistime: {}'.format(thistime))
            print('alertname:{}'.format(level))
            print('job is {}'.format(job))
            if job in contact_list.keys():
                if level == 'p1':
                    print('dingdingcontent:{}'.format(content))
                    resp = DingDingHandler.http_post(webhook, content)
                    print(resp)
                elif level == 'p2':
                    contact = contact_list.get(job)[1]
                    mailaddr = contact + '@xxkeji.com'
                    mailaddrlist = []
                    subject = "基础服务报警"
                    mailaddrlist.append(mailaddr)
                    mailhand = MailHandler()
                    mailhand.sendmail(mailaddrlist, subject, alertinf)
                elif level == 'p0':
                    content_prefix = config.smsprefix +' \n'
                    content = content_prefix + alertinf
                    smshand = SmsHandler()
                    smshand.sendsms(contacts, content)


api.add_resource(mailApi, '/api/v1/sender/mail')
api.add_resource(dingDingApi, '/api/v1/sender/dingding')
api.add_resource(falconDingDingApi, '/api/v1/sender/falcondingding')
api.add_resource(smsApi, '/api/v1/sender/sms')
api.add_resource(GrafanaSmsApi, '/api/v1/sender/grafanasms')
api.add_resource(GrafanaTelApi, '/api/v1/sender/grafanatel')
api.add_resource(GrafanaDingDingApi, '/api/v1/sender/grafanadingding')
api.add_resource(GrafanaMailApi, '/api/v1/sender/grafanamail')
api.add_resource(AlertManagerApi, '/api/v1/sender/alertmanager')

if __name__ == '__main__':
    app.run(host=FHOST, port=FPORT)
