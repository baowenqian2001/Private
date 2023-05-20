# -*- coding: utf-8 -*-
import sys
import uuid
import requests
import wave
import base64
import hashlib

import json

from imp import reload

import time

reload(sys)

YOUDAO_URL = 'https://openapi.youdao.com/iseapi'
APP_KEY = '6b4a05dd541a7bf7'
APP_SECRET = 'nnELiVjOQhNPBth6KA7rmUtTvzdI4BNK'

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

def parseJson(content):
    score = {'total': content["overall"],
        'accuracy': content["pronunciation"],
        'fluency': content["fluency"],
        'integrity': content["integrity"]
        }
    return score

def connect(audioPath, audioText):
    audio_file_path = audioPath
    lang_type = 'en'
    extension = audio_file_path[audio_file_path.rindex('.')+1:]
    if extension != 'wav':
        print('不支持的音频类型')
        sys.exit(1)
    wav_info = wave.open(audio_file_path, 'rb')
    sample_rate = wav_info.getframerate()
    nchannels = wav_info.getnchannels()
    wav_info.close()
    with open(audio_file_path, 'rb') as file_wav:
        q = base64.b64encode(file_wav.read()).decode('utf-8')

    data = {}
    data['text'] = audioText
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

    response = do_request(data)
    content = json.loads(response.content)
    # score = parseJson(content)
    return content

# if __name__ == '__main__':
#     connect(r"E:\projects\speech\backend\data\WAVE\SPEAKER0001\1679381840736.wav", "I MADE IT JUST IN TIME.")