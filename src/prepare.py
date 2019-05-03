#%%
# prepare path
import os
import re
import time
import pickle
import sys

rootpath = os.getcwd() + "\\"
srcpath = rootpath + "src\\"
datapath = rootpath + "data\\"
wikipath = datapath + "wiki-pages-text\\"
bm25path = datapath + "bm25.pickles\\"
wikilist = os.listdir(wikipath)

#%%
# prepare train claims
train_set = open("D:\\Documents\\WSTA\\data\\train.json", 'r')
train_json = json.load(train_set)
i = 0
sent_list = []
for (k, v) in train_json.items():
    claim = v['claim']
    claim = claim.replace('-', ' ')
    line = {"sentence" : claim}
    sent_list.append(line)
    i += 1
    if(i % 10000 == 0):
        print(i)

with open("D:\\Documents\\WSTA\\data\\claims.pickle", 'wb') as sent_out:
    pickle.dump(sent_list, sent_out)
    print("claims pickle dumped")

with open("D:\\Documents\\WSTA\\data\\claims.pickle", 'rb') as sent_in:
    claims = pickle.load(sent_in, encoding='utf-8')
    print("claims pickle loaded")

#%%
# prepare querys depending on ners
with open(datapath + "ner.pickle", 'rb') as ner_in:
    ners = pickle.load(ner_in)
    querys = []
    for ner in ners:
        entitys = ner[1]
        querys += [e[0] for e in entitys]

with open(datapath + "querys.pickle", 'wb') as querys_out:
    pickle.dump(querys, querys_out)
    print("querys dumped")

#%%
# prepare wiki text indexing
import os
import time
import json
import pickle

start = time.time()
indexing = {}
# {"1928":["001", "002", "003"]}
for wikiname in wikilist:
    print(wikiname)
    with open(wikipath + wikiname, 'r', encoding='utf-8') as wikifile:
        line_num = 0
        for line in wikifile.readlines():
            line_num += 1
            prevt = None
            words = line.split()
            topic = words[0][:4]
            linei = words[1]
            try:
                indexing[topic].add(wikiname[5:8])
            except KeyError:
                indexing[topic] = set()
                indexing[topic].add(wikiname[5:8])
                
    with open(datapath + "index.pickle", 'wb') as pickle_out:
        pickle.dump(indexing, pickle_out)
    check = time.time()
    print((check - start) / 60.0)
print("done")

json_index = {}
for (t, s) in indexing.items():
    l = list(s)
    json_index[t] = l
with open("D:\\Documents\\WSTA\\data\\index.json", 'w') as json_out:
    json.dump(json_index, json_out)
    print("index dumped")
