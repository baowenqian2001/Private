import os 
import json
import random
import copy
import requests

from fastapi import APIRouter
from fastapi import File, UploadFile
from config.base import Base
from schema.wav import Wav, Item
from api import youdao, xfyun, dataprocess, gopt_compute

# initial router object
router = APIRouter()

@router.get("/api/")
def read_root():
    return "Hello ICALL"

@router.get("/api/senGen")
def randomSentence():
    with open("data/resource/scores.json", "r", encoding="utf-8") as fp:
        text_dict = json.load(fp)
    key, value = random.choice(list(text_dict.items()))
    phonemes = []
    temp = {}
    for word in value["words"]:
        for i in range(len(word["phones"])):
            temp["phoneme"] = word["phones"][i]
            temp["pronunciation"] = word["phones-accuracy"][i] * 50
            phonemes.append(copy.deepcopy(temp))
        word["phonemes"] = phonemes.copy()
        temp.clear()
        phonemes.clear()
    return {"value": value, "path": "SPEAKER" + key[1:5] + "/" + key + ".WAV"}

@router.post("/api/storefile")
async def store_wav_file(file: UploadFile):
    contents = await file.read()
    if not os.path.exists(Base.AUDIO_DIC):
        os.makedirs(Base.AUDIO_DIC)
    with open(os.path.join(Base.AUDIO_DIC, file.filename), "wb") as f:
        f.write(contents)
    return {"filename": file.filename}

@router.post("/api/xfyun")
async def xfyun(wav: Wav):
    audio_path = os.path.join(Base.AUDIO_DIC, wav.wav_name)
    # 总分 准确度 完整度 流利度
    scores = []
    # 讯飞云评测
    model = "讯飞"
    data = xfyun.connect(audio_path, wav.wav_text)
    score = {
        "model": model,
        "data": data,
    }
    scores.append(score)
    # 尚未统一分数度量
    return {"scores": scores}

@router.post("/api/youdao")
async def yd(wav: Wav):
    audio_path = Base.AUDIO_DIC + "/" + wav.wav_name
    content = youdao.connect(audio_path, wav.wav_text)
    return content

@router.post("/api/gopt")
async def gopt(wav: Wav):
    dataprocess.gopt_pre_process(wav.wav_name, wav.wav_text)
    content = gopt_compute.compute()
    return content

@router.post("/api/check")
async def check(item:Item): #该处仅测试时注释
    text = item.text
    data = {"text": text}
    check_res = requests.post("http://202.112.194.65:8080/check/", data=json.dumps(data))
    return json.loads(check_res.content)

# @app.post("/api/chisheng")
# async def cs(wav: Wav):
#     audio_path = "test_collect/" + wav.wav_name
#     content = chisheng(audio_path, wav.wav_text)
#     return content