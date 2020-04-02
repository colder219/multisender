## 提供各种发送接口,目前支持短信和邮件

### python 依赖
> 需要python3环境

```
Flask==1.0.2
Flask-RESTful==0.3.6
uWSGI==2.0.17
requests==2.22.0

```

### 使用说明
调试的话可以使用以下命令直接启动

    python3 multi_sender.py

生产环境建议使用uwsgi启动

    uwsgi uwsgi.ini


### 使用方式 

发送邮件
多个邮箱按','隔开

curl http://multisender.xxkeji.com/api/v1/sender/mail -d 'tos=xxx@163.com,xxx@qq.com&subject=疫情情况报警&content=美国新冠肺炎人数超过1亿，有望在疫苗问世之前，提前实现群体免疫'


发送短信
多个手机号按','隔开

curl http://multisender.xxkeji.com/api/v1/sender/sms -d 'tos=18888888888,19999999999&content=你的服务器CPU使用率已超过99%，公安正在抓你的路上'

### open-falcon 相关配置
> 写这个当初主要是为了open-falcon的告警发送，这里写写一下open-falcon 上需要做的配置

编辑 open-falcon/alarm/config/cfg.json

```
"sms": "http://multisender.xxkeji.com/api/v1/sender/sms",
"mail": "http://multisender.xxkeji.com/api/v1/sender/mail",

```

### falcon 钉钉支持
> 好多业务开发人员不看邮件短信，而且单独配置也比较麻烦，不同的业务组都有钉钉群，报到群里是比较合适的做法，
目前大部分给falcon提供钉钉报警的都是通过falcon回调onealert的接口，我看了一下就算是个人版也要收费，而且配置麻烦，
这里通过falcon的im来实现钉钉报警

首先要将uic.user表中im字段长度改为256使其能存储钉钉的webhook

    ALTER TABLE `uic`.`user` CHANGE COLUMN `im` `im` VARCHAR(256) NOT NULL DEFAULT '' ;

然后修改用户的im的im,信息为钉钉的webhook，为了不影响其它群，可以给比较重要的群配置单独的用户，这里说一下，如果报警组支持im就更好了

![](https://raw.githubusercontent.com/colder219/picbed/master/images/xvx2020-04-0214.30.59.jpg)

然后修改alarm配置文件，如下，重启即可

    "im": "http://multisender.icocofun.net/api/v1/sender/falcondingding",


### 通用钉钉支持
> 原生钉钉支持，默认markdown 需要自己定义报警内容
http://multisender.xxkeji.com/api/v1/sender/dingding
参数 四个
* webhook 钉钉报警链接
* content 报警内容
* title 标题
* 联系人 @人的时候用，填电话号码，多个用',隔开' 这一项不是必填项

具体使用如下

    curl http://multisender.xxkeji.com/api/v1/sender/dingding -d 'webhook=https://oapi.dingtalk.com/robot/send?access_token=76e9ed0663cfe37d1603ed115b795eb730009aa60694a332dc832addfd4c3c35&content=今天天气不错&title=测试&contact=18101243983,18613861638'

    

### grafna支持

#### 短信
grafana 的报警通道选择webhook, 请求方法选择POST  url填下面的 具体看下面的钉钉配置的截图

    http://multisender.xxkeji.com/api/v1/sender/grafanasms
    

电话号码填在message哪里，多个用逗号隔开


#### 电话
grafana 的报警通道选择webhook, 请求方法选择POST  url填下面的

    http://monitor.icocofun.net:8002/api/v1/sender/grafanatel

其它同短信，短信只能报6位数字，仅供叫醒作用
    


#### 钉钉
grafana自带的钉钉报警有两个问题

* 报警channel填写钉钉的机器人地址，不同的群需要创建不同的channel，随着业务组的增多和细分，channel的数量不可控制
* 报警内容不够详细，尤其对于多个变量的面板，比如5xx报警，只能展示出有报警，不能展示出具体那个接口

这里通过调用message参数来获取机器人的地址（message是我们自己填的，意义不大，关注另一个参数ruleName，还有metic就行）解决了第一个问题
第二个问题，通过grafana的请求参数evalMaches来获取详细信息

使用方法如下

alert channel 选择webhook 然后填写接口地址,最右的已经创建好，直接用就可以了，其它grafana自行添加

     http://multisender.xxkeji.com/api/v1/sender/grafanadingding
     
我现在只要配置三个channel 就行了
![](https://raw.githubusercontent.com/colder219/picbed/master/images/xvx2020-04-0216.10.59.jpg)

     
钉钉channel配置如图
![](https://raw.githubusercontent.com/colder219/picbed/master/images/xvx2020-04-0216.13.02.jpg)

然后在每个报警的alert里面配置机器人
message 填写机器人地址
![](https://raw.githubusercontent.com/colder219/picbed/master/images/xvx2020-04-0216.14.40.jpg)

短信和电话大概也一致，号码用逗号隔开
![](https://raw.githubusercontent.com/colder219/picbed/master/images/xvx2020-04-0216.17.40.jpg)

然后重启alarm 模块就可以了

## alertmangaer 支持

只需要在alert中配置报警接口就行，由于alermanager可定制化比较高，有问题可以联系我支持
```
    alertmanager.yml
    receivers:
- name: 'web.hook'
  webhook_configs:
  - url: 'http://multisender.xxkeji.com/api/v1/sender/alertmanager'
```
    


