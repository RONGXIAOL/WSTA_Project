import nltk
from nltk import pos_tag, word_tokenize, edit_distance, jaccard_distance
from nltk.corpus import wordnet
import os
import configure
from editdistance import distance
import time
from difflib import SequenceMatcher
import json
from unicodedata import normalize
import sys

# s = nltk.word_tokenize("Liverpool F.C. was managed by Bill Shankly.")
# r = nltk.pos_tag(s)
# print(r)

# s1 = "The Boston Celtics"
# s2 = "Boston Celtics"
# r1 = edit_distance(s1, s2)
# print(r1)

# word = "3"
# print(word.islower())
# print(word.isalnum())

# tag_word = "co-starts"
# wnl = nltk.stem.wordnet.WordNetLemmatizer()
# new_word = wnl.lemmatize(tag_word, wordnet.VERB)
# print(tag_word, new_word)

# dumplist = os.listdir(configure.DUMPPATH)
# with open(configure.JSONPATH + "test.txt", 'w', encoding='utf-8') as test_out:
#         test_out.writelines(dumplist)
#         print("test dumped")

f = open(configure.DUMPPATH + configure.DUMPLIST[0], 'r', encoding='utf-8')
ls = f.readlines()
s = sum([sys.getsizeof(l) for l in ls])
print(s / 224492)
lg = len(ls)
print(lg)
ls = f.readlines()
lg = len(ls)
print(lg)
f.close()