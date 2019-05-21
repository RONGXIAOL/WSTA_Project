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
from similar import similarity
from pprint import pprint
from ner import get_keywords

# s = nltk.word_tokenize("Liverpool F.C. co-stars managed by Bill Shankly.")
# r = nltk.pos_tag(s)
# print(r)

# tag_word = "co-starts"
# wnl = nltk.stem.wordnet.WordNetLemmatizer()
# new_word = wnl.lemmatize(tag_word, wordnet.VERB)
# print(tag_word, new_word)


# s1 = "I have been to Australia this February"
# s2 = "The second album of Danny Brown was named XX"
# l1 = word_tokenize(s1)
# l2 = word_tokenize(s2)
# p1 = pos_tag(l1)
# p2 = pos_tag(l2)
# pprint(p1)
# pprint(p2)

# [0, 24357, 64724, 12427, 4036, 1754, 742, 189, 29, 2]
s = 'Chris Pine appeared in Wonder Woman (2017 film)'
s = re.sub(r'\([\w\d]+?\)', '', s)
print(s)