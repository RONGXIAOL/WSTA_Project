import os
import re
import io
import sys
import time
import json
import pickle
import configure
from pprint import pprint
from unicodedata import normalize
from nltk.stem.wordnet import WordNetLemmatizer
from index import get_wiki, get_doc, trim
from sent import sent_sim
from ner import parse_claim_entitys, extract_info, weight, word_similarity
from ner import remove_articles, get_keywords, query_doc, load_unig_entity

wnl = WordNetLemmatizer()
mode = None
name = None
answ_file = None
docs_file = None
json_file = None
ners_file = None
mode_name = {
    configure.DEV_MODE: 'DEV',
    configure.NEI_MODE: 'NEI',
    configure.REF_MODE: 'REF',
    configure.SUP_MODE: 'SUP',
    configure.TRN_MODE: 'TRN',
    configure.TST_MODE: 'TST'
}
VERB_WEIGHT = 0.4
NOUN_WEIGHT = 0.3
ADJV_WEIGHT = 0.2
MISC_WEIGHT = 0.1

def do_file(mode=configure.DEV_MODE):
    global answ_file
    global docs_file
    global json_file
    global ners_file
    if (mode == configure.DEV_MODE):
        answ_file = configure.DEV_ANSW
        docs_file = configure.DEV_DOCS
        json_file = configure.DEV_JSON
        ners_file = configure.DEV_NERS
    elif (mode == configure.TST_MODE):
        answ_file = configure.TST_ANSW
        docs_file = configure.TST_DOCS
        json_file = configure.TST_JSON
        ners_file = configure.TST_NERS
    elif (mode == configure.TRN_MODE):
        answ_file = configure.TRN_ANSW
        docs_file = configure.TRN_DOCS
        json_file = configure.TRN_JSON
        ners_file = configure.TRN_NERS
    elif (mode == configure.SUP_MODE):
        answ_file = configure.SUP_ANSW
        docs_file = configure.SUP_DOCS
        json_file = configure.SUP_JSON
        ners_file = configure.SUP_NERS
    elif (mode == configure.REF_MODE):
        answ_file = configure.REF_ANSW
        docs_file = configure.REF_DOCS
        json_file = configure.REF_JSON
        ners_file = configure.REF_NERS
    elif (mode == configure.NEI_MODE):
        answ_file = configure.NEI_ANSW
        docs_file = configure.NEI_DOCS
        json_file = configure.NEI_JSON
        ners_file = configure.NEI_NERS
    else:
        raise TypeError('Mode {mode} not exist, exiting...')


def eval_sent():
    scores = [0] * 11
    name = mode_name[mode]
    with io.open(configure.INSPPATH + 'dev_inspect.json', 'r', encoding='utf-8-sig') as insp_file:
        data = json.load(insp_file)
        print(f'{name} data loaded')
    count = 0
    for key, entry in data.items():
        count += 1
        if(count % 100 == 0):
            print(count)
        claim = entry['claim']
        sents = entry['sents']
        if(len(sents) == 0):
            continue
        claim = claim[:-1]
        c_keywords = get_keywords(claim)
        c_document, topic = extract_info(sents)
        topic_words = set(trim(topic).split())
        c_keywords = [ckw for ckw in c_keywords if ckw[0] not in topic_words]
        ret = []
        for key, content in c_document.items():
            s_keywords = get_keywords(content)
            s_keywords = [skw for skw in s_keywords if skw[0] not in topic_words]
            score = sent_sim(c_keywords, s_keywords)
            ret.append([key, score])
            index = max(0, score - 0.01)
            index = int(index * 10)
            scores[index] += 1
        ret = sorted(ret, key=lambda r: r[1], reverse=True)
        entry['score'] = ret

    with open(configure.INSPPATH + 'dev_score_inspect', 'w', encoding='utf-8') as score_out:
        json.dump(data, score_out)
        print("dev score dumped")
    print(scores)


def eval_docs():
    with open(json_file, 'r', encoding='utf-8') as data_in:
        data = json.load(data_in)
        print(f'{name} data loaded')
    with open(docs_file, 'r', encoding='utf-8') as docs_in:
        docs = json.load(docs_in)
        print(f'{name} docs loaded')
    TP = FP = FN = 0
    for key, entry in data.items():
        if(entry['label'] == 'NOT ENOUGH INFO'):
            continue
        evidence = entry['evidence']
        gold_docs = [e[0] for e in evidence]
        wood_docs = docs[key]['fdocs']
        true_docs = [g for g in gold_docs if g in wood_docs]
        TP += len(true_docs)
        FP += len(wood_docs) - len(true_docs)
        FN += len(gold_docs) - len(true_docs)
    print(TP, FP, FN)
    print('precision = {}'.format(TP / (TP + FP)))
    print('recall = {}'.format(TP / (TP + FN)))


def main():
    global mode
    mode = configure.DEV_MODE
    global name
    name = mode_name[mode]
    print(f'Start in ***{name}*** mode')
    do_file(mode=mode)
    # eval_sent()
    eval_docs()

if __name__ == "__main__":
    main()