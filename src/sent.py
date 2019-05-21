import os
import re
import sys
import time
import json
import pickle
import configure
from unicodedata import normalize
from query import remove_articles, query_doc
from pprint import pprint
from ner import parse_claim_entitys, get_keywords, extract_info, weight
from similar import similarity

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

def do_file(mode=configure.DEV_MODE):
    global answ_file
    global docs_file
    global json_file
    global ners_file
    if (mode == configure.DEV_MODE):
        answ_file = configure.DEV_ANSW
        docs_file = configure.DEV_JSON
        json_file = configure.DEV_JSON
        ners_file = configure.DEV_NERS
    elif (mode == configure.TST_MODE):
        answ_file = configure.TST_ANSW
        docs_file = configure.TST_JSON
        json_file = configure.TST_JSON
        ners_file = configure.TST_NERS
    elif (mode == configure.TRN_MODE):
        answ_file = configure.TRN_ANSW
        docs_file = configure.TRN_JSON
        json_file = configure.TRN_JSON
        ners_file = configure.TRN_NERS
    elif (mode == configure.SUP_MODE):
        answ_file = configure.SUP_ANSW
        docs_file = configure.SUP_JSON
        json_file = configure.SUP_JSON
        ners_file = configure.SUP_NERS
    elif (mode == configure.REF_MODE):
        answ_file = configure.REF_ANSW
        docs_file = configure.REF_JSON
        json_file = configure.REF_JSON
        ners_file = configure.REF_NERS
    elif (mode == configure.NEI_MODE):
        answ_file = configure.NEI_ANSW
        docs_file = configure.NEI_JSON
        json_file = configure.NEI_JSON
        ners_file = configure.NEI_NERS
    else:
        raise TypeError('Mode {mode} not exist, exiting...')


def check_file():
    if(answ_file and docs_file and json_file and ners_file):
        return
    raise ValueError(
        'Path to save files not set, call do_file() with mode argument specified')


def reset_file():
    answ_file = None
    docs_file = None
    json_file = None
    ners_file = None


def sent_sim(ckw, skw):
    cwords = [c[0] for c in ckw]
    swords = [s[0] for s in skw]
    w_score = 0
    for sw in skw:
        if(sw[0] in cwords):
            w_score += weight(sw)
    return w_score


def pick_sents(claim, sents):
    c_keywords = get_keywords(claim)
    c_document = extract_info(sents)
    ret = []
    for key, content in c_document.items():
        s_keywords = get_keywords(content)
        score = sent_sim(c_keywords, s_keywords)
        ret.append([key, score, content])
    ret = sorted(ret, key=lambda r: r[1], reverse=True)
    # ret = [r for r in ret if r[1] > 0]
    ret = [r for r in ret if r[1] > configure.RAW_THRE]
    # ret = [r for r in ret if r[1] > configure.SIM_THRE]
    return ret


def do_answ(dev, answer):
    check_file()
    todump = {}
    for key, entry in dev.items():
        claim = entry['claim']
        label = answer[key]['label']
        evidence = answer[key]['evidence']
        evidence = sorted(evidence, key=lambda s: s[1][1], reverse=True)[
            :configure.TOP_THRE]
        answer[key]['evidence'] = evidence
        # evidence = [[normalize('NFD', e[0]), int(e[1][0])] for e in evidence if (e[1][1] < configure.SIM_THRE)]
        evidence = [[normalize('NFD', e[0]), int(e[1][0])] for e in evidence]
        todump[key] = {
            'claim': claim,
            'label': label,
            'evidence': evidence
        }
    with open(answ_file, 'w', encoding='utf-8') as answer_out:
        json.dump(todump, answer_out)
        print("answer dumped")
    if(mode != configure.TST_MODE):
        with open(configure.DATAPATH + 'check_answer.json', 'w', encoding='utf-8') as check_out:
            json.dump(answer, check_out)
            print("check dumped")
    reset_file()


def do_ners():
    check_file()
    claim_entitys = {}
    with open(configure.DEV_JSON, 'r', encoding='utf-8') as dev_in:
        dev = json.load(dev_in)
        for key, entry in dev.items():
            claim = entry['claim'][:-1]
            entitys = parse_claim_entitys(claim)
            claim_entitys[key] = entitys

    with open(ners_file, 'w', encoding='utf-8') as entitys_out:
        json.dump(claim_entitys, entitys_out)
        print("entitys dumped")


def do_docs():
    check_file()
    with open(ners_file, 'r', encoding='utf-8') as entitys_in:
        entitys = json.load(entitys_in)
        print("entitys loaded")
    with open(configure.TRM_PICK, 'rb') as trimed_in:
        trimed = pickle.load(trimed_in)
        print("trimed loaded")
    with open(configure.CAP_JSON, 'r', encoding='utf-8') as cap_in:
        capital = json.load(cap_in)
        print("capital loaded")
    with open(json_file, 'r', encoding='utf-8') as dev_in:
        dev = json.load(dev_in)
        print("dataset loaded")
    count = 0
    claim_docs = {}
    start = time.time()
    for key, entry in entitys.items():
        count += 1
        if(count % 1000 == 0):
            point = time.time()
            print(count, (point-start)/60)
        query = entitys[key]
        noart = remove_articles(query)
        noart = [n for n in noart if n not in query]
        qdocs = query_doc(query, trimed, capital)
        ndocs = query_doc(noart, trimed, capital)
        ndocs = [(n[0], n[1]+1) for n in ndocs]
        fdocs = qdocs + ndocs
        fdocs = sorted(fdocs, key=lambda tup: tup[1])
        if(len(fdocs) > configure.TOP_THRE):
            fdocs = [f for f in fdocs if f[1] is 0]
        fdocs = [f[0] for f in fdocs]
        claim = dev[key]['claim']
        claim_docs[key] = {
            "claim": claim,
            "fdocs": fdocs
        }
    with open(docs_file, 'w', encoding='utf-8') as docs_out:
        json.dump(claim_docs, docs_out)
        print("docs dumped")
    do_wiki()


def do_wiki():
    interval = []
    doc_wiki = [None] * len(configure.DUMPLIST)
    check_file()
    with open(configure.INT_PICK, 'rb') as int_in:
        interval = pickle.load(int_in)
        print("interval loaded")
    with open(docs_file, 'r', encoding='utf-8') as dev_doc_in:
        dev_docs = json.load(dev_doc_in)
        print("docs loaded")
    for key, entry in dev_docs.items():
        fdocs = entry['fdocs']
        for doc in fdocs:
            wiki = get_wiki(doc, interval)
            try:
                doc_wiki[wiki].append((doc, key))
            except AttributeError:
                doc_wiki[wiki] = []
                doc_wiki[wiki].append((doc, key))

    with open(configure.DWK_PICK, 'wb') as doc_wiki_out:
        pickle.dump(doc_wiki, doc_wiki_out)
        print("doc wiki dumped")


def do_sent():
    check_file()
    with open(json_file, 'r', encoding='utf-8') as dev_in:
        dev = json.load(dev_in)
        print("dev set loaded")
    with open(configure.DWK_PICK, 'rb') as doc_wiki_in:
        doc_wiki = pickle.load(doc_wiki_in)
        print("doc wiki loaded")
    answer = {}
    for key, entry in dev.items():
        answer[key] = entry
        answer[key]['evidence'] = []
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
                if(count % 100 == 0):
                    check = time.time()
                    print(count, (check - start) / 60.0)
                topic = doc[0]
                d_key = doc[1]
                claim = dev[d_key]['claim']
                sents = get_doc(topic, lines)
                if(not sents):
                    continue
                sents = pick_sents(claim, sents)
                evidence = [[topic, s] for s in sents]
                answer[d_key]['evidence'] += evidence
        # if(count > 100):
            # break
    do_answ(dev, answer)


def main():
    mode = configure.DEV_MODE
    name = mode_name[mode]
    print(f'Start in ***{name}*** mode')
    # do_file(mode=mode)
    # do_ners()
    # do_docs()
    # do_sent()


if __name__ == "__main__":
    main()
