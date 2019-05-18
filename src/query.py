import os
import re
import sys
import time
import json
import pickle
import configure
from collections import Counter
from editdistance import distance

articles = {'The', 'A'}
topics = []
trimed = []

def remove_articles(original_ent):
    ret = []
    for ent in original_ent:
        new_ent = [word for word in ent.split() if word not in articles]
        new_ent = ' '.join(new_ent)
        ret.append(new_ent)
    return ret

def query_doc(query, trimed, capital):
    ret = []
    for q in query:
        try:
            fchar = q[0]
        except IndexError:
            continue
        try:
            minid = capital[fchar]['mini']
            maxid = capital[fchar]['maxi']
        except KeyError:
            continue
        for t in trimed[minid : maxid]:
            tpc = t[0]
            trm = t[1]
            score = abs(len(trm) - len(q))
            if(score < configure.LEN_DIFF):
                q = q.replace(' ', '_')
                if(q.find(trm) != -1 or trm.find(q) != -1):
                    ret.append((tpc, score))
    return ret

if __name__ == "__main__":
    with open(configure.NER_JSON, 'r') as entitys_in:
        entitys = json.load(entitys_in)
        print("entitys loaded")
    with open(configure.TRM_PICK, 'rb') as trimed_in:
        trimed = pickle.load(trimed_in)
        print("trimed loaded")
    with open(configure.CAP_JSON, 'r', encoding='utf-8') as cap_in:
        capital = json.load(cap_in)
        print("capital loaded")
    count = 0
    start = time.time()
    for key, entry in entitys.items():
        count += 1
        if(count > 100):
            sys.exit(0)
        query = entitys[key]
        noart = remove_articles(query)
        noart = [n for n in noart if n not in query]
        qdocs = query_doc(query)
        ndocs = query_doc(noart)
        ndocs = [(n[0], n[1]+1) for n in ndocs]
        fdocs = qdocs + ndocs
        fdocs = sorted(fdocs, key=lambda tup:tup[1])
        if(len(fdocs) > configure.TOP_THRE):
            fdocs = [f for f in fdocs if f[1] is 0]
        print(count, query, fdocs)
        check = time.time()
        print((check - start) / 60.0)
