import time
import json
import pickle
import sys
import configure
import nltk
import pprint
from nltk.corpus import wordnet

puncs = {':', '.', '&', '%'}

def is_verb(tag_word, tag_type):
    if(not tag_word.islower()):
        return False
    if(tag_type[0] == 'V'):
        return True
    wnl = nltk.stem.wordnet.WordNetLemmatizer()
    new_word = wnl.lemmatize(tag_word, wordnet.VERB)
    if(new_word != tag_word):
        return True
    return False

def get_first_entity(ptags):
    ret = ""
    count = 0
    for tag in ptags:
        tag_word = tag[0]
        tag_type = tag[1]
        if(tag_word in puncs):
            ret = ret.strip()
            ret += tag_word
            count += 1
            continue
        if(not tag_word[0].isalnum()):
            break
        if(is_verb(tag_word, tag_type)):
            break
        if(tag_type == 'POS'):
            break
        if(tag_type == 'RB' or (len(tag_word) > 2 and tag_word[-2:] == 'ly')):
            break
        ret += tag_word + ' '
        count += 1
    return [ret.strip()], ptags[count:]

def get_rest_entitys(remain_ptags):
    ret = []
    tmp = ""
    for tag in remain_ptags:
        tag_word = tag[0]
        tag_type = tag[1]
        if(tag_word in puncs):
            tmp.strip()
            tmp += tag_word
            continue
        if(not tag_word[0].isalpha()):
            if(tmp is not ""):
                ret.append(tmp.strip())
                tmp = ""
            continue
        if(not tag_word.islower()):
            tmp += tag_word + ' '
        elif(tmp is not ""):
            ret.append(tmp.strip())
            tmp = ""
        else:
            continue
    if(tmp is not ""):
        ret.append(tmp.strip())
    return ret

def parse_claim_entitys(claim):
    ret = []
    claim = nltk.word_tokenize(claim)
    ptags = nltk.pos_tag(claim)
    first_entity, remain_ptags = get_first_entity(ptags)
    rest_entitys = get_rest_entitys(remain_ptags)
    ret = first_entity + rest_entitys
    ret = [r for r in ret if r is not ""]
    return ret

def do_train():
    claim_entitys = {}
    with open(configure.TRN_JSON, 'r') as train_in:
        train = json.load(train_in)
        count = 0
        for key, entry in train.items():
            count += 1
            claim = entry['claim'][:-1]
            entitys = parse_claim_entitys(claim)
            claim_entitys[key] = entitys
            if(count % configure.TRN_STEP == 0):
                check = time.time()
                print(count, (check - start) / 60.0)

    with open(configure.JSONPATH + 'entitys.json', 'w') as entitys_out:
        json.dump(claim_entitys, entitys_out)
        print("entitys dumped")    

if __name__ == "__main__":
    print()