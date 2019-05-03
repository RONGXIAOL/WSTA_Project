import os
import re
import sys
import time
import json
import pickle
from collections import Counter

rootpath = os.getcwd() + "\\"
srcpath = rootpath + "src\\"
datapath = rootpath + "data\\"
wikipath = datapath + "wiki-pages-text\\"
wikilist = os.listdir(wikipath)
querys2doc_path = datapath + "querys2doc\\"
TOP_K = 5

# ner entry
# [
#     'Nikolaj Coster-Waldau worked with the Fox Broadcasting Company.', 
#     [
#         ['Nikolaj Coster Waldau', 'PER'], 
#         ['Fox Broadcasting Company', 'ORG']
#     ]
# ]

with open(datapath + "querys.pickle", 'rb') as querys_in:
    qs = pickle.load(querys_in)
    querys = {}
    token_query_map = {}
    for q in qs:
        if(q not in querys):
            querys[q] = Counter()
        for w in q.split():
            if(w not in token_query_map):
                token_query_map[w] = q
print("done")

# with open(datapath + "tqmap.json", 'w') as tqmap_out:
#     json.dump(token_query_map, tqmap_out)
#     print("tqmap dumped")


def trim_content(content):
    content = content.replace('-LRB-', '')
    content = content.replace('-RRB-', '')
    content = content.replace('-LSB-', '')
    content = content.replace('-RSB-', '')
    content = content.replace('-LCB-', '')
    content = content.replace('-RCB-', '')
    content = content.replace('-COLON-', '')
    content = content.replace('\'\'', '')
    content = content.replace('``', '')
    content = content.replace('--', '')
    content = content.replace('_', ' ')
    content = content.replace('-', ' ')
    return content

start = time.time()
topics = {}
# {"1996_BellSouth_Open":[file, start_line, end_line]}
    
for wikiname in wikilist:
    qt_map = {}
    # {"Nikolaj Coster Waldau": {entry: count}}
    print(wikiname)
    with open(wikipath + wikiname, 'r', encoding='utf-8') as wikifile:
        line_num = 0
        for line in wikifile.readlines():
            line_num += 1
            prevt = None
            words = line.split()
            topic = words[0]
            linei = words[1]
            try:
                topics[topic][2] += 1
            except KeyError:
                topics[topic] = [wikiname[5:8], line_num, line_num + 1]
            start_char = len(str(topic)) + len(str(linei)) + 2
            content = topic + ' ' + line[start_char:]
            content = trim_content(content)
            # if(line_num % 10000 == 0):
            #     print(line_num)

            tokens = content.split()
            for token in tokens:
                query = token_query_map.get(token)
                if (query is None):
                    continue
                exist = re.findall(query, content)
                if(exist):
                    c = querys[query]
                    l = len(exist)
                    c[topic] += l
        
        for (q, c) in querys.items():
            c = c.most_common(TOP_K)

    with open(querys2doc_path + wikiname[5:8] + ".pickle", 'wb') as tmp_out:
        pickle.dump(querys, tmp_out)

    with open(datapath + "querys2doc.json", 'w') as json_out:
        json.dump(querys, json_out)

    with open(datapath + "topics.pickle", 'wb') as topics_out:
        pickle.dump(topics, topics_out)

    with open(datapath + "querys2doc.pickle", 'wb') as querys_out:
        pickle.dump(querys, querys_out)

    check = time.time()
    print((check - start) / 60.0)