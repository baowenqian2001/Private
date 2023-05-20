# -*- coding: UTF-8 -*-
import json
import threading
from websocket import create_connection

cn_url = "wss://wscn-edu.hivoice.cn/ws/eval/mp3"
test2_text = "He found a ball, a toy car, a sticky sweet and a dusty sock"


class Client:

    def __init__(self):
        self.eof = "gnh-test-end"
        self.ws = create_connection(cn_url)
        self.trecv = threading.Thread(target=self.recv)
        self.trecv.start()

    def send(self):

        first_msg = json.dumps({
          "EvalType": "sentence",
          "Language":"cn",
          "displayText": "今天天气怎么样",
          "appkey": "omalbsszqosmvobofhxa2bi3ksfwex7x743ux7qg@eda0d610066a390ac85452fcbcc92319",
          "scoreCoefficient": "1",
          "userID": "YZS16802529390985777",
          "audioFormat": "mp3",
          "eof": "gnh-test-end"
        })
        self.ws.send(first_msg)

        file_object = open(r"D:\毕业设计\ise_ws_python3_demo(讯飞)\ise_ws_python3_demo\ise_ws_python3_demo\cn\read_sentence_cn.mp3", "rb")
        while True:
            chunk = file_object.read(1000)
            if not chunk:
                break
            self.ws.send(chunk)
            # time.sleep(0.01)

        self.ws.send(self.eof)
        # print("audio send end")

    def recv(self):
        result = str(self.ws.recv())
        if len(result) == 0:
            print("receive result end")
            return
        result_dict = json.loads(result)
        # 解析结果
        print(result)

    def close(self):
        self.ws.close()
        # print("websocket connection closed")


if __name__ == '__main__':
    client = Client()
    client.send()
    client.close()
