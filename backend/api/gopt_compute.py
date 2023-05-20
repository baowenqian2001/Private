import torch
import sys
import os
import numpy as np
import copy

from collections import OrderedDict
sys.path.append(os.path.abspath('/home/bwq2019/workspace/gopt_chain/src'))
from models import GOPT

def compute():
    # kaldi gop_speech762
    #step1 = os.system('cd /home/xm2022/projects/kaldi/egs/gop_speechocean762/s5 && bash run.sh')
    
    # 提取gop特征
    #step2 = os.system('cd /home/xm2022/projects/kaldi/egs/gop_speechocean762/s5 && python local/extract_gop_feats.py')

    #step3 = os.system('cd /home/xm2022/projects/gopt && mkdir data/raw_kaldi_gop/speechdata && cp -r /home/xm2022/projects/kaldi/egs/gop_speechocean762/s5/gopt_feats/* data/raw_kaldi_gop/speechdata')

    #step4 = os.system('cd /home/xm2022/projects/gopt && mkdir data/seq_data_speechdata && cd src/prep_data && python gen_seq_data_phn.py')
    
    # 清算单词数及单词对应的音素数
    word_num = 0
    word_phone = []
    with open ("/home/bwq2019/workspace/data/so_cn/test/text", "r") as f:
        for line in f:
            all_word = line.strip("\n").split("	")[1].split(" ")

    with open("/home/bwq2019/workspace/data/so_cn/resource/text-phone", "r") as f:
        for line in f:
            phone_num = len(line.strip("\n").split(" ")[1:])
            word_phone.append([all_word[word_num], phone_num])
            word_num += 1

    
    # 根据特征算得分

    gopt = GOPT(embed_dim=24, num_heads=1, depth=3, input_dim=82)
    # GOPT is trained with dataparallel, so it need to be wrapped with dataparallel even you have a single gpu or cpu
    # gopt = torch.nn.DataParallel(gopt)
    # sd = torch.load('/home/xm2022/projects/gopt/exp/result_0214/gopt-1e-3-3-1-25-24-gopt-librispeech-br-0/models/best_audio_model.pth', map_location='cpu')
    sd = torch.load('/home/bwq2019/workspace/gopt_chain/exp/gopt-1e-3-3-1-25-24-gopt-chinese_chain-br-2/models/best_audio_model.pth', map_location='cpu')

    new_sd = OrderedDict()
    for k in sd.keys():
        new_k = ".".join(k.split(".")[1:])
        new_sd[new_k] = sd[k]

    gopt.load_state_dict(new_sd, strict=True)

    te_label = np.loadtxt('/home/xm2022/projects/gopt/data/raw_kaldi_gop/speechdata/te_labels_phn.csv', delimiter=',', dtype=str)
    result = {}
    input_feat = np.load("/home/xm2022/projects/gopt/data/seq_data_speechdata/te_feat.npy")
    input_phn = np.load("/home/xm2022/projects/gopt/data/seq_data_speechdata/te_label_phn.npy")
    gopt = gopt.float()
    gopt.eval()
    with torch.no_grad():
        t_input_feat = torch.from_numpy(input_feat[:,:,:])
        t_phn = torch.from_numpy(input_phn[:,:,0])
        u1, u2, u3, u4, u5, p, w1, w2, w3 = gopt(t_input_feat.float(),t_phn.float())
        
        result['accuracy'] = u1.item()*50
        result['completeness'] = u2.item()*50
        result['fluency'] = u3.item()*50
        result['prosodic'] = u4.item()*50
        result['total'] = u5.item()*50
        result['words'] = []

        phonemes = []
        temp = {}
        index = 0
        word_index = 0
        for item in word_phone:
            result['words'].append({"text" : item[0]})
            for i in range(item[1]):
                temp["phoneme"] = te_label[index + i]
                temp["pronunciation"] = w3[0][index + i].item()*50
                phonemes.append(copy.deepcopy(temp))
            index = index + i + 1
            result["words"][word_index]["phonemes"] = phonemes.copy()
            # result["words"].append({"phonemes" : phonemes.copy()})
            word_index += 1
            temp.clear()
            phonemes.clear()

    #清理计算时产生的文件 
    step6 = os.system('sh /home/xm2022/projects/speech/backend/api/clean.sh')
    return(result)

# if __name__ == '__main__':
#     # gopt_pre_process("1679483892968.WAV", "LOOK AT JOHN'S SWEATER")
#     compute()