import os
import re
import sys
import time
import json
import pickle
import configure
from pprint import pprint
from unicodedata import normalize
from nltk.stem.wordnet import WordNetLemmatizer
from index import get_wiki, get_doc, trim
from ner import parse_claim_entitys, extract_info, weight, word_similarity
from ner import remove_articles, get_keywords, query_doc, load_unig_entity

wnl = WordNetLemmatizer()
mode = None
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


def check_file():
    if(answ_file and docs_file and json_file and ners_file):
        return
    raise ValueError(
        'Path to save files not set, call do_file() with mode argument specified')


def reset_file():
    global answ_file
    global docs_file
    global json_file
    global ners_file
    answ_file = None
    docs_file = None
    json_file = None
    ners_file = None


def words_sim(cwords, swords):
    if(len(cwords) == 0):
        return 0.0
    ret = 0.0
    for cw in cwords:
        max_sim = 0.0
        for sw in swords:
            sim = word_similarity(sw, cw)
            max_sim = max(sim, max_sim)
        ret += max_sim
    ret = ret / len(cwords)
    return ret


def sent_sim(ckw, skw):
    cverbs = [c[0] for c in ckw if c[1][0] == 'V']
    cnouns = [c[0] for c in ckw if c[1][0] == 'N']
    cadjvs = [c[0] for c in ckw if c[1][0] in {'J', 'R'}]
    cother = [c[0] for c in ckw if c[0] not in (cnouns + cverbs + cadjvs)]
    cverbs = [wnl.lemmatize(c, 'v') for c in cverbs]
    cnouns = [wnl.lemmatize(c, 'n') for c in cnouns]
    cadjvs = [wnl.lemmatize(c, 'r') for c in cadjvs]
    cadjvs = [wnl.lemmatize(c, 'a') for c in cadjvs]

    sverbs = [s[0] for s in skw if s[1][0] == 'V']
    snouns = [s[0] for s in skw if s[1][0] == 'N']
    sadjvs = [s[0] for s in skw if s[1][0] in {'J', 'R'}]
    sother = [s[0] for s in skw if s[0] not in (snouns + sverbs + sadjvs)]
    sverbs = [wnl.lemmatize(s, 'v') for s in sverbs]
    snouns = [wnl.lemmatize(s, 'n') for s in snouns]
    sadjvs = [wnl.lemmatize(s, 'r') for s in sadjvs]
    sadjvs = [wnl.lemmatize(s, 'a') for s in sadjvs]

    vscore = VERB_WEIGHT * words_sim(cverbs, sverbs)
    nscore = NOUN_WEIGHT * words_sim(cnouns, snouns)
    ascore = ADJV_WEIGHT * words_sim(cadjvs, sadjvs)
    oscore = MISC_WEIGHT * words_sim(cother, sother)

    vinuse = int(bool(len(cverbs) > 0))
    ninuse = int(bool(len(cnouns) > 0))
    ainuse = int(bool(len(cadjvs) > 0))
    oinuse = int(bool(len(cother) > 0))
    
    wscore = vscore * vinuse + nscore * ninuse + ascore * ainuse + oscore * oinuse
    try:
        wscore = wscore / (VERB_WEIGHT * vinuse + NOUN_WEIGHT *
                       ninuse + ADJV_WEIGHT * ainuse + MISC_WEIGHT * oinuse)
    except ZeroDivisionError:
        wscore = 0.0
        print(ckw, skw)
    assert(wscore <= 1)
    return wscore


def pick_sents(claim, sents):
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
        content = topic + ' ' + key + ' ' + content
        ret.append([key, score, content])
    ret = sorted(ret, key=lambda r: r[1], reverse=True)
    # ret = [r for r in ret if r[1] > 0]
    # ret = [r for r in ret if r[1] > configure.RAW_THRE]
    ret = [r for r in ret if r[1] > configure.SIM_THRE]
    return ret


def do_answ(dev, answer):
    check_file()
    todump = {}
    for key, entry in dev.items():
        claim = entry['claim']
        label = "SUPPORTS"
        evidence = answer[key]['evidence']
        score = [e[1][1] for e in evidence]
        sents = [e[1][2] for e in evidence]
        evidence = sorted(evidence, key=lambda s: s[1][1], reverse=True)[
            :configure.TOP_THRE]
        answer[key]['evidence'] = evidence
        evidence = [[normalize('NFD', e[0]), int(e[1][0])] for e in evidence]
        todump[key] = {
            'claim': claim,
            'label': label,
            'evidence': evidence,
            'score' : score,
            'sents' : sents
        }
    with open(answ_file, 'w', encoding='utf-8') as answer_out:
        json.dump(todump, answer_out)
        print("answer dumped")
    reset_file()


def do_ners():
    check_file()
    claim_entitys = {}
    load_unig_entity()
    with open(json_file, 'r', encoding='utf-8') as dev_in:
        dev = json.load(dev_in)
        count = 0
        for key, entry in dev.items():
            count += 1
            if(count % 1000 == 0):
                print(count)
            claim = entry['claim']
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
    count_docs = 0
    start = time.time()
    for key, entry in entitys.items():
        count += 1
        if(count % 100 == 0):
            point = time.time()
            print(count, (point-start)/60)
        query = entitys[key]
        noart = remove_articles(query)
        qdocs = query_doc(query, trimed, capital)
        ndocs = query_doc(noart, trimed, capital)
        ndocs = [(n[0], n[1]+1) for n in ndocs]
        fdocs = qdocs + ndocs
        fdocs = sorted(fdocs, key=lambda tup: tup[1])
        if(len(fdocs) > configure.TOP_THRE):
            fdocs = [f for f in fdocs if f[1] is 0]
            # fdocs = [f for f in fdocs if f[1] < configure.DIF_SIZE]
        fdocs = [f[0] for f in fdocs]
        claim = dev[key]['claim']
        claim_docs[key] = {
            "claim": claim,
            "fdocs": fdocs
        }
        count_docs += len(fdocs)
    with open(docs_file, 'w', encoding='utf-8') as docs_out:
        json.dump(claim_docs, docs_out)
        print("docs dumped")
        print(f'{count_docs} docs in total')
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
        answer[key] = {
            'claim': entry['claim'],
            'label': 'SUPPORTS',
            'evidence': [],
            'sents' : [],
            'score' : []
        }
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
    global mode
    mode = configure.DEV_MODE
    name = mode_name[mode]
    print(f'Start in ***{name}*** mode')
    do_file(mode=mode)
    # do_ners()
    # do_docs()
    do_wiki()
    # do_sent()


if __name__ == "__main__":
    main()