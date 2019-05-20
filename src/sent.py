import os
import re
import sys
import time
import json
import pickle
import configure
from unicodedata import normalize
from query import remove_articles, query_doc
from index import get_doc, get_wiki, trim
from pprint import pprint
from ner import parse_claim_entitys, get_keywords, extract_info, weight


def sent_sim(ckw, skw, cj, sj):
    cwords = [c[0] for c in ckw]
    cptags = [c[1] for c in ckw]
    swords = [s[0] for s in skw]
    sptags = [s[1] for s in skw]
    j1_score = cj ^ sj
    j2_score = cj and sj
    w_score = 0
    for sw in skw:
        if(sw[0] in cwords):
            w_score += weight(sw)
    return w_score


def pick_sents(claim, sents):
    c_keywords, cvnum, cbnum = get_keywords(claim)
    c_judge = not bool(cvnum - cbnum)
    c_document = extract_info(sents)
    ret = []
    for key, content in c_document.items():
        s_keywords, svnum, sbnum = get_keywords(content)
        s_judge = not bool(svnum - sbnum)
        score = sent_sim(c_keywords, s_keywords, c_judge, s_judge)
        ret.append([key, score, content])
    ret = sorted(ret, key=lambda r: r[1], reverse=True)
    # ret = [r for r in ret if r[1] > 0]
    ret = [r for r in ret if r[1] > configure.RAW_THRE]
    return ret


def refine_choice(evidence):
    evidence = sorted(evidence, key=lambda e: e[1][1])
    return evidence


def do_answer(dev, answer, mode=configure.DEV_MODE):
    todump = {}
    for key, entry in dev.items():
        claim = entry['claim']
        label = answer[key]['label']
        evidence = answer[key]['evidence']
        evidence = sorted(evidence, key=lambda s: s[1][1], reverse=True)[:configure.TOP_THRE]
        # try:
        #     maxscore = evidence[0][1][1]
        # except IndexError:
        #     pass
        # evidence = [[e[0], [e[1][0], e[1][1]/maxscore]] for e in evidence]
        answer[key]['evidence'] = evidence
        # evidence = [[normalize('NFD', e[0]), int(e[1][0])] for e in evidence if (e[1][1] < configure.SIM_THRE)]
        evidence = [[normalize('NFD', e[0]), int(e[1][0])] for e in evidence]
        todump[key] = {
            'claim': claim,
            'label': label,
            'evidence': evidence
        }
    answ_file = None
    if(mode == configure.TST_MODE):
        answ_file = configure.TST_ANSW
    with open(answ_file, 'w', encoding='utf-8') as answer_out:
        json.dump(todump, answer_out)
        print("answer dumped")
    if(mode == configure.DEV_MODE):
        with open(configure.DATAPATH + 'check_answer.json', 'w', encoding='utf-8') as check_out:
            json.dump(answer, check_out)
            print("check dumped")


def do_ner(mode=configure.DEV_MODE):
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


def do_doc(mode=configure.DEV_MODE):
    json_file = None
    docs_file = None
    ners_file = None
    if(mode == configure.TST_MODE):
        json_file = configure.TST_JSON
        docs_file = configure.TST_DOCS
        ners_file = configure.TST_NERS
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
    do_wiki(mode=mode)


def do_wiki(mode=configure.DEV_MODE):
    interval = []
    doc_wiki = [None] * len(configure.DUMPLIST)
    docs_file = None
    if(mode == configure.TST_MODE):
        docs_file = configure.TST_DOCS
    with open(configure.INT_PICK, 'rb') as int_in:
        interval = pickle.load(int_in)
        print("interval loaded")
    with open(docs_file, 'r') as dev_doc_in:
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


def do_sent(mode=configure.DEV_MODE):
    json_file = None
    if(mode == configure.TST_MODE):
        json_file = configure.TST_JSON
    with open(json_file, 'r', encoding='utf-8') as dev_in:
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
                    # do_answer(dev, answer, mode=mode)
                    # sys.exit(0)
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
    do_answer(dev, answer, mode=mode)


if __name__ == "__main__":
    # do_wiki(configure.TST_MODE)
    do_sent(mode=configure.TST_MODE)
    # do_sent(mode=configure.TST_MODE)
