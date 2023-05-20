from youdao import connect
import json
import os
import time
#加载讯飞数据
xunfei = {}
with open('result.txt') as f:
    lines = f.readlines()
    for line in lines:
        line = line.strip().split(' ')
        #print(line)
        y = json.loads(''.join(line[1:]))
        for k,v in y.items():#字符串格式的数字转换为浮点型数字
            if k != 'prosodic':
                y[k] = float(v)
        xunfei[line[0]] = y
        #xunfei.append(y)

if __name__ == '__main__':
    #path = r'D:\毕业设计\ise_ws_python3_demo(讯飞)\ise_ws_python3_demo\ise_ws_python3_demo\cn\read_sentence_cn.wav'
    #text = '今天天气怎么样'
    #加载文本文件
    dirname = '/home/bwq2019/workspace/data/so_cn/WAVE'########adjust
    text_path = '/home/bwq2019/workspace/data/aidatatang_200zh/transcript/aidatatang_200_zh_transcript.txt'
    text2phone_path = '/home/bwq2019/workspace/毕业设计/text-phone.txt'
    all_score_dict = {}
    text_dict = {}
    result_already = []
    '''if os.path.exists(text2phone_path):
        with open(text2phone_path,"r") as f:    #设置文件对象 
            lines = f.readlines()
            for line in lines:
                line = line.strip().split(' ')
                result_already.append(line[0][:-2])'''
    with open('scores.json') as f1:
        lines = f1.readlines()
        line = json.loads(lines[-1])
        result_already = line.keys()
    with open(text_path,"r") as f:   #设置文件对象 
        lines = f.readlines()
        for line in lines:
            line = line.strip().split(' ')
            text_dict[line[0]] = ''.join(line[1:])

    # path = '/home/bwq2019/workspace/data/so_cn/WAVE/G5639/T0055G5639S0038.wav'
    # text = '我去准备等下要PRESENTATION等下聊'
    num = 0
    for root,dirs,files in os.walk(dirname):#获取说话人编号dirs
        for name in files:
            if name[:-4] not in result_already:
                if name.endswith('.wav'): 
                    num += 1
                    print("get:",num,':',name)
                    #if num >= 6:
                    #    num = 0
                    path = os.path.join(root,name)
                    text =  text_dict[name[:-4]] #'\uFEFF'+
                    youdao_dict,text2phone = connect(path,text)
                    time.sleep(1) 
                    '''with open('text-phone.txt','a+') as f:
                        for i in range(len(text2phone)):
                            f.writelines([name[:-4]+'.',str(i+1),' ',text2phone[i],'\n'])'''
                    youdao_dict['prosodic'] = xunfei[name[:-4]]["prosodic"]
                    youdao_dict['completeness'] = round(xunfei[name[:-4]]["completeness"]*0.1) #+讯飞
                    youdao_dict['fluency'] = round(xunfei[name[:-4]]["fluency"]*0.1)#+讯飞
                    youdao_dict['total'] = round(xunfei[name[:-4]]["total"]*0.1)#+讯飞
                    all_score_dict[name[:-4]] = youdao_dict
                    #print("get:",name)
                    #if num >= 271:
    with open('scores_ori.json','a+') as fr:
        json.dump(all_score_dict,fr,ensure_ascii=False)
        fr.writelines(['\n'])
    #num = 0
    #result_already = []
    '''with open('/home/bwq2019/workspace/毕业设计/text-phone.txt',"r") as f:    #设置文件对象 
        lines = f.readlines()
        for line in lines:
            line = line.strip().split(' ')
            result_already.append(line[0][:-2])
    time.sleep(30)'''
