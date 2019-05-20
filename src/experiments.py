import nltk
from nltk import pos_tag, word_tokenize
from nltk.corpus import wordnet
import os
import configure
from editdistance import distance
import time
from difflib import SequenceMatcher
import json
from unicodedata import normalize
import sys
from pprint import pprint

s = nltk.word_tokenize("Liverpool F.C. co-stars managed by Bill Shankly.")
r = nltk.pos_tag(s)
print(r)

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

s1 = "I have been to Australia this year"
s2 = "The second album of Danny Brown was named XXX"
l1 = word_tokenize(s1)
l2 = word_tokenize(s2)
p1 = pos_tag(l1)
p2 = pos_tag(l2)
pprint(p1)
pprint(p2)
