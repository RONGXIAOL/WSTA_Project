import os
import re
import sys
import time
import json
import pprint
import pickle
import configure
from collections import Counter
from bisect import bisect_left, bisect_right
from unicodedata import normalize


def trim(topic):
    topic = re.sub(r'_-LRB-.*?-RRB-', '', topic)
    topic = re.sub(r'_-LSB-.*?-RSB-', '', topic)
    topic = re.sub(r'_-LCB-.*?-RCB-', '', topic)
    topic = topic.replace('-COLON-_', ': ')
    topic = topic.replace('_', ' ')
    return topic


def sort_by_wiki():
    intervals = []
    count = 0
    for wiki in configure.WIKILIST:
        with open(configure.WIKIPATH + wiki, 'r', encoding='utf-8') as wikifile:
            lines = wikifile.readlines()
            lcopy = lines
            lines = [[id, line.split()] for id, line in enumerate(lines)]
            lines = sorted(lines, key=lambda l: l[1][0])
            mini = lines[0][1][0]
            maxi = lines[-1][1][0]
            intervals.append((mini, maxi))
            index = [line[0] for line in lines]
            lines = [lcopy[idx] for idx in index]
            with open(configure.SORTPATH + wiki[5:8] + ".sorted.txt", 'w', encoding='utf-8') as sorted_wiki:
                sorted_wiki.write("mini = {}\n".format(mini))
                sorted_wiki.write("maxi = {}\n".format(maxi))
                for line in lines:
                    sorted_wiki.write(line)
        count += 1
        print(count)
    with open(configure.SORTPATH + "intervals.txt", 'w', encoding='utf-8') as intervals_out:
        for mini, maxi in intervals:
            intervals_out.write("mini = {}, maxi = {}\n".format(mini, maxi))
        print("intervals dumped")


def adjust_margin(chunk, lines):
    if(len(chunk) == 0 or len(lines) == 0):
        return chunk, lines
    prev_maxi = chunk[-1].split()[0]
    count = 0
    for line in lines:
        curr_mini = line.split()[0]
        if(curr_mini == prev_maxi):
            count += 1
            chunk.append(line)
    return chunk, lines[count:]


def sort_by_corpus():
    offset = 8
    length = len(configure.WIKILIST)
    # length = 10
    lines = []
    sortlist = os.listdir(configure.SORTPATH)
    cut_size = configure.CUT_SIZE
    interval = []
    for i in range(offset):
        with open(configure.SORTPATH + sortlist[i], 'r', encoding='utf-8') as sorted_wiki_in:
            lines += sorted_wiki_in.readlines()
    count = 0
    start = time.time()
    for i in range(length - offset):
        with open(configure.SORTPATH + sortlist[i+offset], 'r', encoding='utf-8') as sorted_wiki_in:
            delta = sorted_wiki_in.readlines()
            lines += delta
            cut_size = len(delta)
        lcopy = lines
        lines = [[id, line.split()] for id, line in enumerate(lines)]
        lines = sorted(lines, key=lambda l: l[1][0])
        index = [line[0] for line in lines]
        lines = [lcopy[idx] for idx in index]
        chunk = lines[:cut_size]
        lines = lines[cut_size:]
        chunk, lines = adjust_margin(chunk, lines)
        mini = chunk[0].split()[0]
        maxi = chunk[-1].split()[0]
        interval.append((mini, maxi))
        with open(configure.DUMPPATH + sortlist[i][0:3] + ".sorted.txt", 'w', encoding='utf-8') as sorted_wiki:
            sorted_wiki.write("mini = {}\n".format(mini))
            sorted_wiki.write("maxi = {}\n".format(maxi))
            for line in chunk:
                sorted_wiki.write(line)
        count += 1
        print(count)
        check = time.time()
        print((check - start) / 60.0)
        if(len(lines) == 0):
            break
    cut_size = configure.CUT_SIZE
    for i in range(offset):
        filename = '000' + str(count + 1)
        filename = filename[-3:]
        chunk = lines[:cut_size]
        lines = lines[cut_size:]
        chunk, lines = adjust_margin(chunk, lines)
        mini = chunk[0].split()[0]
        maxi = chunk[-1].split()[0]
        interval.append((mini, maxi))
        with open(configure.DUMPPATH + filename + '.sorted.txt', 'w', encoding='utf-8') as sorted_wiki:
            sorted_wiki.write("mini = {}\n".format(mini))
            sorted_wiki.write("maxi = {}\n".format(maxi))
            for line in chunk:
                sorted_wiki.write(line)
            count += 1
            print(count)
            if(len(lines) == 0):
                break
    if(len(lines) > 0):
        lastfile = '000' + str(count + 1)
        lastfile = lastfile[-3:]
        with open(configure.DUMPPATH + lastfile + '.sorted.txt', 'w', encoding='utf-8') as sorted_wiki:
            sorted_wiki.write("mini = {}\n".format(mini))
            sorted_wiki.write("maxi = {}\n".format(maxi))
            for line in lines:
                sorted_wiki.write(line)
            count += 1
            print(count)
    with open(configure.PICKPATH + "interval.pickle", 'wb') as interval_out:
        pickle.dump(interval, interval_out)
        print("interval dumped")
    with open(configure.JSONPATH + "interval.txt", 'w', encoding='utf-8') as interval_out:
        for mini, maxi in interval:
            interval_out.write("{} {}".format(mini, maxi))
            interval_out.write('\n')
        print("interval dumped")


def dump_topics():
    topics = []
    configure.DUMPLIST = os.listdir(configure.DUMPPATH)
    try:
        os.remove(configure.JSONPATH + "topics.txt")
    except OSError:
        pass
    count = 0
    for wikiname in configure.DUMPLIST:
        todump = []
        with open(configure.DUMPPATH + wikiname, 'r', encoding='utf-8') as wiki_in:
            lines = wiki_in.readlines()
            prev = lines[2].split()[0]
            for line in lines[2:]:
                curr = line.split()[0]
                if(curr != prev):
                    topics.append(prev)
                    todump.append(prev)
                    prev = curr
            topics.append(curr)
            todump.append(curr)
        with open(configure.JSONPATH + "topics.txt", 'a', encoding='utf-8') as topics_out:
            todump = [(t + '\n') for t in todump]
            topics_out.writelines(todump)
            topics_out.write('\n')
        count += 1
        print(count, sys.getsizeof(topics) / 1024 / 1024)
    with open(configure.PICKPATH + "topics.pickle", 'wb') as topics_out:
        pickle.dump(topics, topics_out)
        print("topics dumped")


def trim_topics():
    with open(configure.TPC_PICK, 'rb') as topics_in:
        topics = pickle.load(topics_in)
        print("topics loaded")
        print("{} topics in total".format(len(topics)))
        trimed = [(t, trim(t)) for t in topics]
        print("topics trimmed")
        print(trimed[:100])
    with open(configure.TRM_PICK, 'wb') as trimed_out:
        pickle.dump(trimed, trimed_out)
        print("trimed dumped")


def dump_capitals():
    trimed = []
    with open(configure.TRM_PICK, 'rb') as trimed_in:
        trimed = pickle.load(trimed_in)
        print("trimed loaded")
    capitals = {}
    count = 0
    for line in trimed:
        fchar = line[0][0]
        try:
            capitals[fchar]['maxi'] += 1
        except KeyError:
            capitals[fchar] = {
                'mini': count,
                'maxi': count + 1
            }
        count += 1
    with open(configure.CAP_JSON, 'w', encoding='utf-8') as cap_out:
        json.dump(capitals, cap_out)
        print("capitals dumped")


def get_wiki(topic, interval):
    wiki = None
    for idx, line in enumerate(interval):
        mini = line[0]
        maxi = line[1]
        if(topic >= mini and topic <= maxi):
            wiki = idx
            break
    if(wiki == None):
        print("{} not found in corpus".format(topic))
        return None
    return wiki


def get_doc(topic, lines):
    lines = lines[2:]
    topic += ' '
    t_len = len(topic)
    lcopy = [l[:t_len] for l in lines]
    lhsid = bisect_left(lcopy, topic)
    rhsid = bisect_right(lcopy, topic)
    try:
        assert(lcopy[lhsid] == topic)
        assert(lcopy[rhsid-1] == topic)
    except AssertionError:
        print(f'{topic} not found, may be unicode inconsistency.')
        return None
    return lines[lhsid:rhsid]
