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
import xml.etree.ElementTree as ET


APPID='5a695d56'
APISecret='MDM0YzllZmIwNGFkNmRlZWVjZTk1ZWZj'
APIKey='a5e2152abdea82fe746ccc93994d36be'

# 第一帧的标识
STATUS_FIRST_FRAME = 0
# 中间帧标识
STATUS_CONTINUE_FRAME = 1
# 最后一帧的标识 
STATUS_LAST_FRAME = 2  


#  BusinessArgs参数常量
SUB = "ise"
ENT = "en_vip"
#中文题型：read_syllable（单字朗读，汉语专有）read_word（词语朗读）read_sentence（句子朗读）read_chapter(篇章朗读)
#英文题型：read_word（词语朗读）read_sentence（句子朗读）read_chapter(篇章朗读)simple_expression（英文情景反应）read_choice（英文选择题）topic（英文自由题）retell（英文复述题）picture_talk（英文看图说话）oral_translation（英文口头翻译）
CATEGORY = "read_sentence"
#待评测文本 utf8 编码，需要加utf8bom 头
TEXT = '\uFEFF' + "WE CALL IT BEAR"
#直接从文件读取的方式
#TEXT = '\uFEFF'+ open("cn/read_sentence_cn.txt","r",encoding='utf-8').read()


class WS_Param(object):
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
        # print("date: ", date)
        # print("v: ", v)
        # print('websocket url :', url)
        return url


class Spider(object):

    def __init__(self, url, wsParam):
        self.url = url 
        self.wsParam  = wsParam
        self.ws = None
        self.xml = None

    def on_open(self, ws):
        """
        Callback object which is called at opening websocket.
        1 argument:
        @ ws: the WebSocketApp object
        """
        # print('************websocket is opened***************')
        def run(*args):
            frameSize = 1280  # 每一帧的音频大小
            intervel = 0.04  # 发送音频间隔(单位:s)
            status = STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧

            with open(self.wsParam.AudioFile, "rb") as fp:
                while True:
                    buf = fp.read(frameSize)
                    # 文件结束
                    if not buf:
                        status = STATUS_LAST_FRAME
                    # 第一帧处理
                    # 发送第一帧音频，带business 参数
                    # appid 必须带上，只需第一帧发送
                    if status == STATUS_FIRST_FRAME:
                        d = {"common": self.wsParam.CommonArgs,
                            "business": self.wsParam.BusinessArgs,
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

    def on_data(self, ws, string, type, continue_flag):
        """
        4 argument.
        The 1st argument is this class object.
        The 2nd argument is utf-8 string which we get from the server.
        The 3rd argument is data type. ABNF.OPCODE_TEXT or ABNF.OPCODE_BINARY will be came.
        The 4th argument is continue flag. If 0, the data continue
        """

    def on_message(self, ws, message):
        """
        Callback object which is called when received data.
        2 arguments:
        @ ws: the WebSocketApp object
        @ message: utf-8 data received from the server
        """
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
                    xml = base64.b64decode(result)
                    #python在windows上默认用gbk编码，print时需要做编码转换，mac等其他系统自行调整编码
                    self.xml = xml.decode("gbk")

        except Exception as e:
            print("receive msg,but parse exception:", e)

    def on_error(self, ws, error):
        """
        Callback object which is called when got an error.
        2 arguments:
        @ ws: the WebSocketApp object
        @ error: exception object
        """
        print(error)

    def on_close(self, ws, close_status_code, close_msg):
        """
        Callback object which is called when the connection is closed.
        2 arguments:
        @ ws: the WebSocketApp object
        @ close_status_code
        @ close_msg
        """
        print('The connection is closed!')

    def start(self):
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_data=self.on_data,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.ws.run_forever()
    
    def parseXML(self):
        # print(self.xml)
        root = ET.fromstring(self.xml)
        for child in root.iter("read_chapter"):
            attr = child.attrib
            accuracy = attr.get("accuracy_score")
            fluency = attr.get("fluency_score")
            integrity = attr.get("integrity_score")
            total = attr.get("total_score")
            score = {'total': total,
                'accuracy': accuracy,
                'fluency': fluency,
                'integrity': integrity
                }
            return score

def connect(audioFile, text):
    time1 = datetime.now()
    #APPID、APISecret、APIKey信息在控制台——语音评测了（流式版）——服务接口认证信息处即可获取
    wsParam = WS_Param(APPID=APPID, APISecret=APISecret, APIKey=APIKey,
                       AudioFile=audioFile, Text=text)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    spider = Spider(url=wsUrl, wsParam=wsParam)
    spider.start()
    score = spider.parseXML()
    time2 = datetime.now()
    # print(time2-time1)
    return score
