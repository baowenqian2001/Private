import json

all_dict = {}
with open('scores_ori.json') as f:
      lines = f.readlines()
      for line in lines[-2:]:
            single_dict = json.loads(line)
            for k,v in single_dict.items():
                  all_dict[k] = v
with open('scores.json','w') as f:
      json.dump(all_dict,f,indent = 2,ensure_ascii=False)