import time
import json
import pickle
import sys
import configure
import nltk
import pprint
import re
from index import trim
from collections import Counter
from nltk.corpus import wordnet
from nltk import pos_tag, word_tokenize

articles = {'The', 'A'}
being = {'am', 'is', 'are', 'was', 'were', 'be', 'being', 'been'}
reals = {
    'CD', 'FW', 'JJ', 'JJR', 'JJS', 'NN', 'NNS', 'NNP', 'NNPS',
    'RB', 'RBR', 'RBS', 'RP', 'VB', 'VBD', 'VBG', 'VBN', 'VBP',
    'VBZ'
}
junks = {
    'CC', 'DT', 'EX', 'IN', 'LS', 'MD', 'PDT', 'POS', 'PRP',
    'PRP$', 'SYM', 'TO', 'UH', 'WDT', 'WP', 'WP$', 'WRB'
}
precs = {
    'CD', 'FW', 'NNP', 'NNPS'
}
verbs = {
    'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'
}

FIRST_ENTITY_LEN = 5
B_SENT = '$$$'
L_SENT = '^^^'
UNIG_ENTITYS = {}


def trim_claim(claim):
    claim = re.sub(r'\([\w\d\s]+?\)', '', claim)
    claim = claim.replace(', ', ' , , ')
    # claim = claim.replace('`', '')
    claim = claim.replace('\'s', ' is')
    # claim = claim.replace('\"', '')
    return claim


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
        for t in trimed[minid: maxid]:
            tpc = t[0]
            trm = t[1]
            score = abs(len(trm) - len(q))
            if(score < configure.DIF_SIZE):
                # q = q.replace(' ', '_')
                if(q.find(trm) != -1 or trm.find(q) != -1):
                    ret.append((tpc, score))
    return ret


def extract_info(sents):
    ret = {}
    for s in sents:
        words = s.split()
        topic = words[0]
        s_num = words[1]
        index = len(topic) + len(s_num) + 2
        content = s[index:]
        # content = content.replace('_', ' ')
        ret[s_num] = content
    return ret


def get_keywords(claim):
    claim = claim.split()
    ptags = pos_tag(claim)
    ret = []
    for tag in ptags:
        tag_word = tag[0]
        tag_type = tag[1]
        # if(tag_type not in reals and tag_type not in junks and tag_type.isalpha()):
        # raise TypeError(f'{tag} not found in Penn TreeBank POS')
        if(tag_type in reals and tag_word.isalnum()):
            ret.append(tag)
    return ret


def weight(w):
    if(w[1] in precs):
        return 3
    if(w[1] in verbs and w[0] not in being):
        return 7
    else:
        return 1


def tags_to_entity(ptags):
    try:
        words = [p[0] for p in ptags]
        ret = ' '.join(words)
    except TypeError:
        # print(ptags)
        return tags_to_entity(ptags[0])
    except IndexError:
        # print(ptags)
        return
    return ret


def is_verb(tag):
    tag_word = tag[0]
    tag_type = tag[1]
    if(not tag_word.islower()):
        return False
    if(tag_type[0] == 'V'):
        return True
    if(tag_type == 'MD'):
        return True
    wnl = nltk.stem.wordnet.WordNetLemmatizer()
    new_word = wnl.lemmatize(tag_word, wordnet.VERB)
    if(new_word != tag_word):
        return True
    return False


def is_adverb(tag):
    if(may_be_entity(tag)):
        return False
    tag_word = tag[0]
    tag_type = tag[1]
    if(tag_type[0] == 'R'):
        return True
    if(tag_word.endswith('ly')):
        return True
    return False


def refine_entity(ptags):
    if(len(ptags) == 1):
        tag = ptags[0]
        tag_word = tag[0]
        tag_type = tag[1]
        if(tag_word in UNIG_ENTITYS.keys()):
            return [tag]
        else:
            return []
    elif(len(ptags) > 5):
        ret = get_rest_entitys(ptags[1:])
        return ret
    else:
        return ptags


def get_first_entity(ptags):
    ret = []
    count = 0
    for tag in ptags:
        tag_word = tag[0]
        tag_type = tag[1]
        if(is_verb(tag)):
            break
        if(is_adverb(tag)):
            break
        ret.append(tag)
        count += 1
    ret = refine_entity(ret)
    return ret, ptags[count:]


def may_be_entity(tag):
    tag_word = tag[0]
    tag_type = tag[1]
    if(tag_word == B_SENT):
        return False
    if(tag_word == L_SENT):
        return False
    if(tag_word.isnumeric()):
        return False
    if(not tag_word.isalpha() and len(tag_word) < 3):
        return False
    if(not tag_word.islower()):
        return True
    return False


def get_rest_entitys(remain_ptags):
    ret = []
    tmp = []
    remain_ptags = [[B_SENT, 'POS']] + remain_ptags + [[L_SENT, 'POS']]
    remain_mbent = [may_be_entity(t) for t in remain_ptags]
    for i in range(len(remain_ptags)):
        tag = remain_ptags[i]
        tag_word = tag[0]
        tag_type = tag[1]
        if(tag_word == B_SENT):
            continue
        if(tag_word == L_SENT):
            break
        l_ent = remain_mbent[i-1]
        r_ent = remain_mbent[i+1]
        c_ent = remain_mbent[i]
        if(l_ent and r_ent or c_ent):
            tmp.append(tag)
        elif(len(tmp) != 0):
            tmp = refine_entity(tmp)
            if(len(tmp) > 0):
                ret.append(tmp)
            tmp = []
        else:
            continue
    if(len(tmp) != 0):
        tmp = refine_entity(tmp)
        if(len(tmp) > 0):
            ret.append(tmp)
    return ret


def parse_claim_entitys(claim):
    ret = []
    claim = trim_claim(claim)[:-1]
    claim = claim.split()
    ptags = nltk.pos_tag(claim)
    ptags = [[p[0], p[1]] for p in ptags]
    first_entity, remain_ptags = get_first_entity(ptags)
    first_entity = [tags_to_entity(first_entity)]
    assert(len(first_entity) == 1)
    rest_entitys = get_rest_entitys(remain_ptags)
    ret = first_entity + [tags_to_entity(r) for r in rest_entitys]
    ret = [r for r in ret if r is not '']
    return ret


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
        try:
            wood_set = wood[key]['entitys']
        except KeyError:
            break
        diff_set = [g for g in gold_set if g not in wood_set]
        if(len(diff_set) == 0):
            continue
        diff[key] = {}
        diff[key]['claim'] = entry['claim']
        diff[key]['diff'] = gold_set + ['$$$$'] + wood_set


    with open(configure.INSPPATH + 'diff_entitys.json', 'w') as entitys_out:
        json.dump(diff, entitys_out)
        print("diff entitys dumped")


if __name__ == "__main__":
    # with open(configure.TRN_JSON, 'r', encoding='utf-8') as json_in:
    #     json_file = json.load(json_in)
    #     print("json loaded")
    # with open(configure.INSPPATH + 'unig_entitys.json', 'r', encoding='utf-8') as unig_in:
    #     UNIG_ENTITYS = json.load(unig_in)
    #     print("unig loaded")
    # wood_entitys = {}
    # count = 0
    # start = time.time()
    # for key, entry in json_file.items():
    #     count += 1
    #     if(count % 10000 == 0):
    #         check = time.time()
    #         print(count, (check - start)/60)
    #     claim = entry['claim']
    #     entitys = parse_claim_entitys(claim)
    #     wood_entitys[key] = {
    #         'claim': claim,
    #         'entitys': entitys
    #     }
    # with open(configure.INSPPATH + 'wood_entitys.json', 'w', encoding='utf-8') as wood_out:
    #     json.dump(wood_entitys, wood_out)
    #     print("wood dumped")
    dump_diff_entitys()
