import json

with open('so.json') as f:
  data = json.load(f)

word = data['000010011']['words']
for key,value in word[0].items():
    print(key,':')
    print(value)