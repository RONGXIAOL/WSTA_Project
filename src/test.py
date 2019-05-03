#%%
import re
import sys
import pickle
import json
from collections import Counter

with open("D:\\Documents\\WSTA\\data\\querys2doc.pickle", 'rb') as q2d_in:
    querys = pickle.load(q2d_in)
    print("q2d loaded")
#%%
TIME = 10
THRE = 10
TOPN = 10
readable = {}
i = 0
for (ner, count) in querys.items():
    i += 1
    if(i % 1000 == 0):
        print(i)
    count = Counter(count)
    count = count.most_common()
    for (k, v) in count:
        vv = v
        kk = k
        # a = b
        if(re.search(r'List_of', k)):
            vv /= TIME
        if(re.search(r'disambiguation', k)):
            vv /= TIME
        kk = kk.replace('_', ' ')
        kk = kk.replace('-', ' ')
        if(kk == ner):
            vv *= TIME
        # if(vv >= THRE):
        try:
            c = readable[ner]
        except KeyError:
            readable[ner] = Counter()
        readable[ner][k] = vv

for(ner, count) in readable.items():
    readable[ner] = readable[ner].most_common(TOPN)

print('done')

#%%
with open("D:\\Documents\\WSTA\\data\\q2d.json", 'w') as q2d_out:
    json.dump(readable, q2d_out)

l = list(readable.items())
for ll in l[::1000]:
    print(ll, '\n')