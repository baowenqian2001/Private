# -*- coding: utf-8 -*-
import sys
import uuid
import requests
import wave
import base64
import hashlib
import json

from importlib import reload

import time

#reload(sys)

YOUDAO_URL = 'https://openapi.youdao.com/iseapi'
APP_KEY = '534e140130834ce6'
APP_SECRET = 'RcEvqupe22a8Q2JLrew3LejRR738vkoG'
so = dict()

def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size-10:size]

def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()

def do_request(data):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post(YOUDAO_URL, data=data, headers=headers)

def single_class(integrity,refText,pronunciation,fluency,overall,words):#传入单词个数
    #sentence process
    sen_labels = ['accuracy','completeness','fluency','prosodic','total','text']
    dict = {}
    dict['accuracy'] = round(pronunciation*0.1)
    dict['completeness'] = integrity#+讯飞
    dict['fluency'] = fluency#+讯飞
    dict['prosodic'] = 0#####################暂定+讯飞
    dict['words'] = words
    dict['total'] = overall#+讯飞
    dict['text'] = refText
    #word process
    #for key,value in dict.items():
    #    print(key,':')
    #    print(value)
    return dict
    # with open('result.txt','w') as f:
    #     f.write(str(dict))####.decode()


def connect(audio_file_path,text):
    audio_file_path = audio_file_path#r'D:\毕业设计\ise_ws_python3_demo(讯飞)\ise_ws_python3_demo\ise_ws_python3_demo\cn\read_sentence_cn.wav'
    lang_type = 'zh-CHS'
    extension = audio_file_path[audio_file_path.rindex('.')+1:]
    # if extension != 'wav':
    #     print('不支持的音频类型')
    #     sys.exit(1)
    wav_info = wave.open(audio_file_path, 'rb')
    sample_rate = wav_info.getframerate()
    nchannels = wav_info.getnchannels()
    wav_info.close()
    with open(audio_file_path, 'rb') as file_wav:
        q = base64.b64encode(file_wav.read()).decode('utf-8')

    data = {}
    data['text'] = text#'今天天气怎么样'
    curtime = str(int(time.time()))
    data['curtime'] = curtime
    salt = str(uuid.uuid1())
    signStr = APP_KEY + truncate(q) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)
    data['appKey'] = APP_KEY
    data['q'] = q
    data['salt'] = salt
    data['sign'] = sign
    data['signType'] = "v2"
    data['langType'] = lang_type
    data['rate'] = sample_rate
    data['format'] = 'wav'
    data['channel'] = nchannels
    data['type'] = 1

    #process result
    single_dict = {}
    response = do_request(data)
    result = response.content.decode()

    result_dict = json.loads(result)
    if result_dict["errorCode"] != '0':
        print(result_dict["errorCode"]) 
    integrity = result_dict['integrity']
    refText = result_dict['refText']
    pronunciation = result_dict['pronunciation']
    fluency = result_dict['fluency']
    overall = result_dict['overall']
    nums_words = len(result_dict['words'])

    words = []
    text2phone = []
    for n in range(nums_words):
        if '\u4e00' <= result_dict['words'][n]['word'] <= '\u9fff':
            single_word = {} 
            phonemes = []
            phones_accuracy  = []
            for i in result_dict['words'][n]['phonemes']:
                if i['phoneme']=='未知单词元素':
                    continue
                phonemes.append(i['phoneme'])
                phones_accuracy.append(round(i['pronunciation']*0.1))
            single_word['accuracy'] = round(result_dict['words'][n]['pronunciation']*0.1)
            single_word['stress'] = 10######################default
            single_word['phones'] = phonemes
            single_word['total'] = round(result_dict['words'][n]['pronunciation'] * 0.1)
            text2phone.append(' '.join(phonemes))
            
            single_word['text'] = result_dict['words'][n]['word']


            single_word['phones-accuracy'] = phones_accuracy
            words.append(single_word)
    dict = single_class(integrity,refText,pronunciation,fluency,overall,words)
    return dict,text2phone
    #with open('result.txt','w') as f:
    #    f.write(result)####.decode()


if __name__ == '__main__':
    path = '/home/bwq2019/workspace/data/so_cn/WAVE/G1107/T0055G1107S0429.wav'
    text = 'A家族'
    youdao_dict,text2phone = connect(path,text)
    #youdao_dict1,text2phone1 = connect(path1,text1)
    print(youdao_dict)
