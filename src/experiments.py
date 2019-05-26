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
import io
import re
import copy
from pprint import pprint
from ner import get_keywords, parse_claim_entitys

# s = nltk.word_tokenize("Liverpool F.C. co-stars managed by Bill Shankly.")
# r = nltk.pos_tag(s)
# print(r)

# tag_word = "geese"
# wnl = nltk.stem.wordnet.WordNetLemmatizer()
# new_word = wnl.lemmatize(tag_word, 'n')
# print(tag_word, new_word)


# s1 = "Valerian and the City of a Thousand Planets's main character is named Laureline".split()
# s2 = "The second album of Danny Brown was named XX"
# p1 = pos_tag(s1)
# p2 = pos_tag(l2)
# pprint(p1)
# pprint(p2)

# entity length
# [0, 24357, 64724, 12427, 4036, 1754, 742, 189, 29, 2]

# key = '186320'
# q = ["The Hunchback of Notre Dame"]
