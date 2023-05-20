# -*- coding:utf-8 -*-
#
#   author: iflytek
#
#  本demo测试时运行的环境为：Windows + Python3.7
#  本demo测试成功运行时所安装的第三方库及其版本如下，您可自行逐一或者复制到一个新的txt文件利用pip一次性安装：
#   cffi==1.12.3
#   gevent==1.4.0
#   greenlet==0.4.15
#   pycparser==2.19
#   six==1.12.0
#   websocket==0.2.1
#   websocket-client==0.56.0
#
#  语音评测流式 WebAPI 接口调用示例 接口文档（必看）：https://www.xfyun.cn/doc/Ise/IseAPI.html
#  错误码链接：https://www.xfyun.cn/document/error-code （code返回错误码时必看）
#  评测示例默认为中文句子题型的示例,其他试题示例请到Demo中查看试题示例与音频示例并注意修改相关评测参数值,到平台文档下方进行音频试题示例下载也可
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
from builtins import Exception, str, bytes

import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
import os

STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识

#  BusinessArgs参数常量
SUB = "ise"
ENT = "cn_vip"
#中文题型：read_syllable（单字朗读，汉语专有）read_word（词语朗读）read_sentence（句子朗读）read_chapter(篇章朗读)
#英文题型：read_word（词语朗读）read_sentence（句子朗读）read_chapter(篇章朗读)simple_expression（英文情景反应）read_choice（英文选择题）topic（英文自由题）retell（英文复述题）picture_talk（英文看图说话）oral_translation（英文口头翻译）
CATEGORY = "read_sentence"
#待评测文本 utf8 编码，需要加utf8bom 头
TEXT = '\uFEFF'+ "今天天气怎么样"
#直接从文件读取的方式
#TEXT = '\uFEFF'+ open("cn/demo1.txt","r",encoding='utf-8').read()
import json
import xmltodict

class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, AudioFile, Text):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.AudioFile = AudioFile
        self.Text = Text

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"category": CATEGORY, "sub": SUB, "ent": ENT, "cmd": "ssb", "auf": "audio/L16;rate=16000",
                             "aue": "raw", "text": self.Text, "ttp_skip": True, "aus": 1}

    # 生成url
    def create_url(self):
        # wws请求对Python版本有要求，py3.7可以正常访问，如果py版本请求wss不通，可以换成ws请求，或者更换py版本
        url = 'ws://ise-api.xfyun.cn/v2/open-ise'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ise-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/open-ise " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ise-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)

        # 此处打印出建立连接时候的url,参考本demo的时候，比对相同参数时生成的url与自己代码生成的url是否一致
        print("date: ", date)
        print("v: ", v)
        print('websocket url :', url)
        return url


# 收到websocket消息的处理
def on_message(ws, message):
    try:
        code = json.loads(message)["code"]
        sid = json.loads(message)["sid"]
        if code != 0:
            errMsg = json.loads(message)["message"]
            print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))

        else:
            data = json.loads(message)["data"]
            status = data["status"]
            result = data["data"]
            if (status == 2):
                kx = {}
                xml = base64.b64decode(result)
                parsed_data = xmltodict.parse(xml.decode('gbk'))
                dict = parsed_data['xml_result']['read_sentence']['rec_paper']['read_sentence']
                kx["completeness"] = dict['@integrity_score']
                kx['fluency'] = dict['@fluency_score']
                kx["prosodic"] = round(float(dict['@phone_score'])*0.1)
                #print(kx["prosodic"],type(kx["prosodic"]))
                kx["total"] = dict['@total_score']
                with open('result.txt', 'a+') as f:
                    json.dump(kx,f)####.decode()
                    f.writelines(['\n'])
                # for key,value in kx.items():
                #     print(key,':')
                #     print(value)
                #python在windows上默认用gbk编码，print时需要做编码转换，mac等其他系统自行调整编码

                #print(xml.decode("gbk"))

    except Exception as e:
        print("receive msg,but parse exception:", e)


# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws):
    print("### closed ###")


# 收到websocket连接建立的处理
def on_open(ws):
    def run(*args):
        frameSize = 1280  # 每一帧的音频大小
        intervel = 0.04  # 发送音频间隔(单位:s)
        status = STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧

        with open(wsParam.AudioFile, "rb") as fp:
            while True:
                buf = fp.read(frameSize)
                # 文件结束
                if not buf:
                    status = STATUS_LAST_FRAME
                # 第一帧处理
                # 发送第一帧音频，带business 参数
                # appid 必须带上，只需第一帧发送
                if status == STATUS_FIRST_FRAME:
                    d = {"common": wsParam.CommonArgs,
                         "business": wsParam.BusinessArgs,
                         "data": {"status": 0}}
                    d = json.dumps(d)
                    ws.send(d)
                    status = STATUS_CONTINUE_FRAME
                # 中间帧处理
                elif status == STATUS_CONTINUE_FRAME:
                    d = {"business": {"cmd": "auw", "aus": 2, "aue": "raw"},
                         "data": {"status": 1, "data": str(base64.b64encode(buf).decode())}}
                    ws.send(json.dumps(d))
                # 最后一帧处理
                elif status == STATUS_LAST_FRAME:
                    d = {"business": {"cmd": "auw", "aus": 4, "aue": "raw"},
                         "data": {"status": 2, "data": str(base64.b64encode(buf).decode())}}
                    ws.send(json.dumps(d))
                    time.sleep(1)
                    break
                # 模拟音频采样间隔
                time.sleep(intervel)
        ws.close()

    thread.start_new_thread(run, ())

if __name__ == "__main__":
    # 测试时候在此处正确填写相关信息即可运行
    #检验已经返回的数据里有没有它
    result_path = '/home/bwq2019/workspace/毕业设计/result.txt'
    result_already = []
    if os.path.exists(result_path):
        with open(result_path,"r") as f:    #设置文件对象 
            lines = f.readlines()
            for line in lines:
                line = line.strip().split(' ')
                result_already.append(line[0])

    dirname = '/home/bwq2019/workspace/data/so_cn/WAVE'
    text_path = '/home/bwq2019/workspace/data/aidatatang_200zh/transcript/aidatatang_200_zh_transcript.txt'
    text_dict = {}
    with open(text_path,"r") as f:    #设置文件对象 
        lines = f.readlines()
        for line in lines:
            line = line.strip().split(' ')
            text_dict[line[0]] = ''.join(line[1:])
    for root,dirs,files in os.walk(dirname):#获取说话人编号dirs
        for name in files:
                if name.endswith('.wav'): 
                    if name[:-4] not in result_already:
                        #if name[:-4] == 'T0055G1450S0149':
                        path = os.path.join(root,name)
                        text = '\uFEFF'+ text_dict[name[:-4]]
                        with open('result.txt', 'a+') as f:
                            f.writelines([name[:-4],' '])
                        time1 = datetime.now()
                        #APPID、APISecret、APIKey信息在控制台——语音评测了（流式版）——服务接口认证信息处即可获取
                        '''wsParam = Ws_Param(APPID='2ca98578', APISecret='NDIxY2Q0ZTdhNmI5OGMwZDFmZTA2MTI1',
                        APIKey='ad532708f7733964b710c18821caa471',
                        AudioFile=path, Text=text)'''
                        wsParam = Ws_Param(APPID='520233ea', APISecret='ZjlhZTQ1OTc4MTI1MTY5OWE2ZGJjODUy',
                                        APIKey='1bfd841145999101400c76d3ff724cee',
                                        AudioFile=path, Text=text)#file_path\text
                        websocket.enableTrace(False)
                        wsUrl = wsParam.create_url()
                        ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
                        ws.on_open = on_open
                        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
                        time2 = datetime.now()
                        print(time2 - time1)
