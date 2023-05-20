a_str = 'nǐ huì yòng sǎo miáo yí ba         \n                            \n          \n你会用扫描仪吧。'

import re
r = re.compile('[\u4e00-\u9fa5]+')

res = r.findall(a_str)  # ['404', 'not', 'found', '23']


print(" ".join(res))
