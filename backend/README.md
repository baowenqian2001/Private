# 后端

## 目录结构
```shell
├── api #后端接口文件
│   ├── chisheng.py #驰声api
│   ├── clean.sh #清理gopt模型计算时产生的文件
│   ├── dataprocess.py #处理数据成gopt模型需要的格式
│   ├── gopt_compute.py #gopt模型计算
│   ├── xfyun.py #讯飞api
│   └── youdao.py #有道api
├── app.py #入口文件
├── config
│   └── base.py #配置文件
├── data #该目录储存gopt模型需要的数据，需要严格按照目录创建
│   ├── resource
│   │   ├── lexicon.txt
│   │   ├── scores-detail.json
│   │   ├── scores.json
│   │   └── text-phone
│   ├── test
│   │   ├── spk2age
│   │   ├── spk2gender
│   │   ├── spk2utt
│   │   ├── text
│   │   ├── utt2spk
│   │   └── wav.scp
│   ├── train
│   └── WAVE
│       └── SPEAKER0001
├── routers
│   └── route.py #接口
└── schema
    └── wav.py #类
```