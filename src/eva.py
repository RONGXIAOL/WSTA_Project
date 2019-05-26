import os
import re
import io
import sys
import time
import json
import pickle
import configure
from nltk import FreqDist
from nltk import pos_tag
from nltk.corpus import brown
from collections import Counter
from ner import trim_claim, parse_claim_entitys, is_verb, remove_articles

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
B_SENT = '$$$'
L_SENT = '^^^'


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
            s_keywords = [
                skw for skw in s_keywords if skw[0] not in topic_words]
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


def find_gold_entitys(entry):
    claim = entry['claim']
    entitys = entry['evidence']
    entitys = [e[0] for e in entitys]
    entitys = list(set(entitys))
    entitys = [(e, trim(e).strip()) for e in entitys]
    entitys = [(e[0], e[1].replace('_', ' ')) for e in entitys]
    ret = [e for e in entitys if (claim.find(e[1]) != -1)]
    if(len(ret) == 0):
        return None
    else:
        return ret


def dump_gold_entitys():
    with open(configure.TRN_JSON, 'r', encoding='utf-8') as json_in:
        json_file = json.load(json_in)
        print("json loaded")
    gold_entitys = {}
    unig_entitys = Counter()
    for key, entry in json_file.items():
        entitys = find_gold_entitys(entry)
        if(not entitys):
            continue
        for e in entitys:
            if(len(e[1].split()) == 1):
                unig_entitys[e[1]] += 1
        gold_entitys[key] = {
            'claim': entry['claim'],
            'entitys': entitys
        }
    with open(configure.INSPPATH + 'gold_entitys.json', 'w', encoding='utf-8') as gold_out:
        json.dump(gold_entitys, gold_out)
        print("gold dumped")
    with open(configure.INSPPATH + 'unig_entitys.json', 'w', encoding='utf-8') as unig_out:
        json.dump(unig_entitys, unig_out)
        print("unig dumped")


def dump_diff_entitys():
    diff = {}
    lens = [0] * 10
    with open(configure.INSPPATH + 'gold_entitys.json', 'r', encoding='utf-8') as gold_in:
        gold = json.load(gold_in)
        print("gold entitys loaded")
    with open(configure.INSPPATH + 'wood_entitys.json', 'r', encoding='utf-8') as wood_in:
        wood = json.load(wood_in)
        print("wood entitys loaded")
    count = 0
    for key, entry in gold.items():
        count += 1
        gold_set = [e[1] for e in entry['entitys']]
        wood_set = wood[key]['entitys']
        wood_art = remove_articles(wood_set)
        wood_set = wood_set + wood_art
        diff_set = [g for g in gold_set if g not in wood_set]
        lens[len(diff_set)] += 1
        if(len(diff_set) == 0):
            continue
        diff[key] = {}
        diff[key]['claim'] = entry['claim']
        diff[key]['diff'] = gold_set + ['$$$'] + wood_set

    with open(configure.INSPPATH + 'diff_entitys.json', 'w') as entitys_out:
        json.dump(diff, entitys_out)
        print("diff entitys dumped")
    print(lens)


def dump_wood_entitys():
    with open(configure.TRN_JSON, 'r', encoding='utf-8') as json_in:
        json_file = json.load(json_in)
        print("json loaded")

    wood_entitys = {}
    count = 0
    start = time.time()
    for key, entry in json_file.items():
        count += 1
        if(count % 1000 == 0):
            check = time.time()
            print(count, (check - start)/60)
        claim = entry['claim']
        entitys = parse_claim_entitys(claim)
        wood_entitys[key] = {
            'claim': claim,
            'entitys': entitys
        }
    with open(configure.INSPPATH + 'wood_entitys.json', 'w', encoding='utf-8') as wood_out:
        json.dump(wood_entitys, wood_out)
        print("wood dumped")


def dump_unigram_blacklist():
    with open(configure.TRN_JSON, 'r', encoding='utf-8') as data_in:
        data = json.load(data_in)
        print("train data loaded")
    unig_entitys = Counter()
    count = 0
    for key, entry in data.items():
        count += 1
        if(count % 1000 == 0):
            print(count)
        claim = entry['claim'][:-1]
        claim = B_SENT + ' ' + claim + ' ' + L_SENT
        claim = trim_claim(claim)
        words = claim.split()
        ptags = pos_tag(words)
        cut = -1
        for idx, w in enumerate(words):
            tag = ptags[idx][1]
            if(tag[0] == 'V' or tag == 'MD'):
                cut = idx
                break
        cut += 1
        words = [B_SENT] + words[cut:]
        for idx, w in enumerate(words):
            if(w == B_SENT):
                continue
            if(w == L_SENT):
                break
            prev_word = words[idx-1]
            next_word = words[idx+1]
            if(prev_word[0].isupper()):
                continue
            if(next_word[0].isupper()):
                continue
            if(w[0].isupper() and w.isalpha()):
                unig_entitys[w] += 1
    unig_probs = unig_entitys.most_common()
    unig_count = len(unig_probs)
    cut_size = int(unig_count / 100)
    blacklist = [u[0] for u in unig_probs[:cut_size]]
    with open(configure.PICKPATH + 'blacklist.pickle', 'wb') as black_out:
        pickle.dump(blacklist, black_out)
        print("unigram blacklist dumped")


def main():
    global mode
    mode = configure.DEV_MODE
    global name
    name = mode_name[mode]
    print(f'Start in ***{name}*** mode')
    do_file(mode=mode)
    # eval_sent()
    # eval_docs()


# if __name__ == "__main__":
    # dump_wood_entitys()
    # dump_diff_entitys()
    # dump_unigram_blacklist()