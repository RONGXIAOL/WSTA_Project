import os
import re
import sys
import time
import json
import pickle
import configure
import unicodedata
from ner import parse_claim_entitys
from query import remove_articles, query_doc
from index import get_doc, get_wiki
from collections import OrderedDict
from pprint import pprint

def do_ner():
    claim_entitys = {}
    with open(configure.DEV_JSON, 'r', encoding='utf-8') as dev_in:
        dev = json.load(dev_in)
        for key, entry in dev.items():
            claim = entry['claim'][:-1]
            entitys = parse_claim_entitys(claim)
            claim_entitys[key] = entitys

    with open(configure.JSONPATH + 'dev_entitys.json', 'w', encoding='utf-8') as entitys_out:
        json.dump(claim_entitys, entitys_out)
        print("entitys dumped")

def do_doc():
    with open(configure.JSONPATH + 'dev_entitys.json', 'r', encoding='utf-8') as entitys_in:
        entitys = json.load(entitys_in)
        print("entitys loaded")
    with open(configure.TRM_PICK, 'rb') as trimed_in:
        trimed = pickle.load(trimed_in)
        print("trimed loaded")
    with open(configure.CAP_JSON, 'r', encoding='utf-8') as cap_in:
        capital = json.load(cap_in)
        print("capital loaded")
    with open(configure.DEV_JSON, 'r', encoding='utf-8') as dev_in:
        dev = json.load(dev_in)
        print("devset loaded")
    count = 0
    claim_docs = {}
    for key, entry in entitys.items():
        count += 1
        if(count % 1000 == 0):
            print(count)
        query = entitys[key]
        noart = remove_articles(query)
        noart = [n for n in noart if n not in query]
        qdocs = query_doc(query, trimed, capital)
        ndocs = query_doc(noart, trimed, capital)
        ndocs = [(n[0], n[1]+1) for n in ndocs]
        fdocs = qdocs + ndocs
        fdocs = sorted(fdocs, key=lambda tup:tup[1])
        if(len(fdocs) > configure.TOP_THRE):
            fdocs = [f for f in fdocs if f[1] is 0]
        
        fdocs = [unicodedata.normalize('NFD', f[0]) for f in fdocs]
        claim = dev[key]['claim']
        claim_docs[key]={
            "claim" : claim,
            "fdocs" : fdocs
        }
    with open(configure.DEV_DOCS, 'w', encoding='utf-8') as docs_out:
        json.dump(claim_docs, docs_out)
        print("docs dumped")

def do_wiki():
    interval = []
    doc_wiki = [None] * len(configure.DUMPLIST)
    with open(configure.INT_PICK, 'rb') as int_in:
        interval = pickle.load(int_in)
        print("interval loaded")
    with open(configure.DEV_DOCS, 'r') as dev_doc_in:
        dev_docs = json.load(dev_doc_in)
        print("dev docs loaded")
    for key, entry in dev_docs.items():
        if(key == '99495'):
            print(key)
        fdocs = entry['fdocs']
        for doc in fdocs:
            wiki = get_wiki(doc[0], interval)
            try:
                doc_wiki[wiki].append((doc, key))
            except AttributeError:
                doc_wiki[wiki] = []
                doc_wiki[wiki].append((doc, key))

    with open(configure.DWK_PICK, 'wb') as doc_wiki_out:
        pickle.dump(doc_wiki, doc_wiki_out)
        print("doc wiki dumped")
        
def do_sent():
    with open(configure.DEV_JSON, 'r', encoding='utf-8') as dev_in:
        dev = json.load(dev_in)
        print("dev set loaded")
    with open(configure.DWK_PICK, 'rb') as doc_wiki_in:
        doc_wiki = pickle.load(doc_wiki_in)
        print("doc wiki loaded")
    answer = dev
    for key, entry in answer.items():
        entry['label'] = 'SUPPORTS'
        entry['evidence'] = []
    count = 0
    start = time.time()
    for index, docsl in enumerate(doc_wiki):
        if(not docsl):
            continue
        index = "000" + str(index+1)
        index = index[-3:]
        wikifile = index + ".sorted.txt"
        with open(configure.DUMPPATH + wikifile, 'r', encoding='utf-8') as wiki_in:
            lines = wiki_in.readlines()
            for doc in docsl:
                count += 1
                if(count % 1000 == 0):
                    check = time.time()
                    print(count, (check - start) / 60.0)
                topic = doc[0]
                d_key = doc[1]
                sents = get_doc(topic, lines)
                evidence = [topic, 0]
                answer[d_key]['evidence'].append(evidence)

    with open(configure.DEV_ANSW, 'w', encoding='utf-8') as answer_out:
        json.dump(answer, answer_out)
        print("answer dumped")

if __name__ == "__main__":
    do_sent()
    
    # with open(configure.DEV_DOCS, 'r', encoding='utf-8') as docs_in:
    # claim_docs = json.load(docs_in)
    # print("dev docs loaded")
    # set1 = set(dev.keys())
    # set2 = set(answer.keys())
    # lost_keys = set1 - set2
    # for key in lost_keys:
    #     count += 1
    #     if(count % 1000 == 0):
    #         print(count)
    #     claim = dev[key]['claim']
    #     label = 'SUPPORTS'
    #     topics = claim_docs[key]['fdocs']
    #     evidence = [[t, 0] for t in topics]
    #     answer[d_key] = {
    #         'claim' : claim,
    #         'label' : label,
    #         'evidence' : evidence
    #     }