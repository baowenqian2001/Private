import requests
import json
import time
import hashlib
import os
import time
from requests_toolbelt.multipart.encoder import MultipartEncoder

def chisheng(audioPath, audioText):
    hostDomain = "eval.cloud.chivox.com"
    host = "https://eval.cloud.chivox.com"
    endpoint = r"/aieval/init?ver=1&traceId=davidjiang002&appkey="
    appkey = "16781582010000ed"
    secretkey = "3004987f61207758d4b98a3c19f1abe9"
    endpoint = f'{endpoint}{appkey}'
    current_milli_timestamp = str(int(round(time.time() * 1000)));
    midResultNumber = 0
    midResultKey = "midResults"
    wordCoreType = "en.word.score"
    wordRefText = "panda"
    sentCoreType = "en.sent.pron"
    sentRefText = audioText
    sentAudio = audioPath
    isReceivedMidResult = False

    sigSourceStr = appkey + current_milli_timestamp + secretkey
    sigmd5 = hashlib.md5(sigSourceStr.encode())
    sigmd5Str = sigmd5.hexdigest()
    authJsonDic = {"applicationId": appkey, "sig": sigmd5Str, "alg": "md5", "timestamp": current_milli_timestamp,
                "userId": "davidtest"}
    #print(authJsonDic);

    url = ''.join([host, endpoint]);
    headers = \
        {
            "Host": hostDomain,
            "Authorization": json.dumps(authJsonDic),
            "Content-Type": "application/json;charset=UTF-8"
        };

    body = \
        {
            "tokenId": "davidjiang001",
            "feed_expired": 1,
            "server_timeout": 60,
            "audio": {
                "audioType": "wav",
                "channel": 1,
                "sampleBytes": 2,
                "sampleRate": 16000
            },
            "request":
                {
                    "coreType": sentCoreType,
                    "refText": sentRefText,
                    "accent": 2,
                    "rank": 100,
                    "attachAudioUrl": 1,
                    "result": {
                        "details": {
                            "ext_cur_wrd": 1
                                    }
                            }
                }
        }
    r = requests.post(url, headers=headers, data=json.dumps(body))
    initReturnJson = json.loads(r.text)
    myRecordId = initReturnJson['recordId']
    myCookie = r.headers['Set-Cookie']

    # feed  audio file by piece
    feedEndpoint = r"/aieval/record/" + myRecordId + "/feed?ver=1&traceId=davidjiang002&appkey="
    feedEndpoint = f'{feedEndpoint}{appkey}'
    bound = "------WebKitFormBoundaryyb1zYhTI38xpQxBK--"
    feedContentType = ''.join(["multipart/form-data;boundary=", bound])
    url = ''.join([host, feedEndpoint])
    #print(url)
    headers = \
        {
            "Host": hostDomain,
            "Authorization": json.dumps(authJsonDic),
            "Cookie": myCookie,
            "Content-Type": feedContentType
        }

    # filePath = "panda.mp3";
    filePath = sentAudio
    binFile = open(filePath, 'rb')
    audioSize = os.path.getsize(filePath)
    lastSize = audioSize % 6400

    if lastSize == 0:
        feedTimes = audioSize // 6400
    else:
        feedTimes = audioSize // 6400 + 1

    i = 0

    while i < feedTimes:
        if i == feedTimes - 1:
            isEnd = 1
            binStream = binFile.read(lastSize)
        else:
            isEnd = 0
            binStream = binFile.read(6400)
        if i % 5 == 0 | isReceivedMidResult:
            multipart_encoder = MultipartEncoder(
                fields={
                    "feed": json.dumps({
                        'seq': i,
                        'end': isEnd
                    }),
                    "fetch": json.dumps({
                        "midseq": midResultNumber
                    }),
                    'data': binStream
                },
                boundary=bound
            )
        else:
            multipart_encoder = MultipartEncoder(
                fields={
                    "feed": json.dumps({
                        'seq': i,
                        'end': isEnd
                    }),
                    'data': binStream
                },
                boundary=bound
            )

        feedResult = requests.post(url, headers=headers, data=multipart_encoder)
        feedResultJson = json.loads(feedResult.text)
        if midResultKey in feedResultJson:
            midResultNumber += 1
            #print(f'middle result:  + {feedResultJson}')
            isReceivedMidResult = True
        else:
            isReceivedMidResult = False
        i += 1
        time.sleep(0.2)

    # get result
    resultEndPoint = r"/aieval/record/" + myRecordId + "/fetch?ver=1&midseq=0&wait=60&traceId=davidjiang002&appkey="
    resultEndPoint = f'{resultEndPoint}{appkey}'
    resultUrl = ''.join([host, resultEndPoint])
    finalResult = requests.get(resultUrl)
    #print(f'final Result: \n  {finalResult.text}')

    # release this evaluation after receiving the final result
    releaseEndPoint = r"/aieval/record/" + myRecordId + "/release?ver=1&traceId=davidjiang002&appkey="
    resultEndPoint = f'{releaseEndPoint}{appkey}'
    # releaseUrl = ''.join([host, releaseEndPoint])
    # ReleaseResult = requests.get(releaseUrl)
    #print(f'release Result:\n {ReleaseResult}')
    # print(type(finalResult.text))
    return json.loads(finalResult.text)

# chisheng("test_collect/1678241387902.wav", "ROLL UP TO THE PARTY LIKE")