import os

root_path = '../'
wiki_pages_path = root_path + 'materials/wiki-pages-text/'
pages_list = os.listdir(wiki_pages_path)
pages_list.sort()

doc_line_indexes = []  # a list of dictionary that saves doc's line id
## [{'1986_NBA_Finals': 1, 
##   '1789_Dobrovolsky': 227,
##   '1596_in_Scotland': 618, ...}, 
##   {...}, ...]

head_pages_index = {}  # first 4 charaters of doc appears in which pages
## {'1986':['../materials/wiki-pages-text/wiki-001.txt', '../materials/wiki-pages-text/wiki-002.txt', '../materials/wiki-pages-text/wiki-003.txt'],
##  '1789':['../materials/wiki-pages-text/wiki-001.txt', '../materials/wiki-pages-text/wiki-002.txt'],
##  '1596':['../materials/wiki-pages-text/wiki-001.txt', '../materials/wiki-pages-text/wiki-002.txt']}

for page_name in pages_list:  # 'wiki-001.txt'
	page_path = wiki_pages_path + page_name  # '../materials/wiki-pages-text/wiki-001.txt'
	with open(page_path,'r',encoding='utf-8') as f:
		doc_line_index = {}  # a dictionary that saves docs' line id :
							 ##  {'1986_NBA_Finals': 1, 
							 ##   '1789_Dobrovolsky': 227,
							 ##   '1596_in_Scotland': 618, ...}
		pre = ''
		lines = f.readlines()
		for line_id, line in enumerate(lines):
			tokens = line.split()  # ['1986_NBA_Finals', '2', 'The', 'Celtics', 'defeated', 'the', 'Rockets', ...]
			doc_name = tokens[0]  # '1986_NBA_Finals'
			if doc_name != pre:  # if there is a new doc that appears first time
				doc_line_index[doc_name] = line_id  # record its line id
				head = doc_name[:4]  # '1986_NBA_Finals' => '1986'
				if head not in head_pages_index:
					head_pages_index[head] = [page_path]
				elif page_path not in head_pages_index[head]:
					head_pages_index[head].append(page_path)
				pre = doc_name
		doc_line_indexes.append(doc_line_index)

import json
import unicodedata
import time

start = time.time()

## input : ("Party_of_Hellenism", 3)
def get_content(doc_name, sent_ids):
	contents = []
	sent_ids = sent_ids
	head = unicodedata.normalize('NFC', doc_name)[:4]
	evidence_pages = head_pages_index[head]
	for evidence_page in evidence_pages:
		wiki_index = int(evidence_page[-7:-4]) - 1
		if doc_name in doc_line_indexes[wiki_index]:
			with open(evidence_page,'r',encoding='utf-8') as f:
				lines = f.readlines()[doc_line_indexes[wiki_index][doc_name]:]
				for line in lines:
					if line.startswith(doc_name):
						for sent_id in sent_ids:
							if line.startswith(doc_name+" "+str(sent_id)+" "):
								contents.append(line)
								doc, _id = line.split()[:2]
								if doc != doc_name or _id != str(sent_id):
									print(wiki_index+1, doc,doc_name,_id,sent_id)
	return contents

## read train set into a dictionary
train_path = root_path + 'materials/devset.json'
save_path = root_path + 'materials/devset_pro_NFC.json'
new_dic = {}
with open(train_path,'r',encoding='utf-8') as f:
	train_dic = json.load(f)
	for _id in train_dic:
		claim = unicodedata.normalize('NFC', train_dic[_id]['claim'])
		label = train_dic[_id]['label']
		evidence_contents = []
		doc_sentids = {}
		for evid in train_dic[_id]['evidence']:
			if evid[0] in doc_sentids:
				doc_sentids[evid[0]].append(evid[1])
			else:
				doc_sentids[evid[0]] = [evid[1]]
		for doc_name in doc_sentids:
			try:
				evidence_contents.extend(get_content(unicodedata.normalize('NFC', doc_name), doc_sentids[doc_name]))
			except Exception as e:
				print(e, doc_name, doc_sentids[doc_name])
		new_dic[_id] = {'claim':claim,'evidence':evidence_contents,'label':label}
				
with open(save_path,'w',encoding='utf-8') as f:
	json.dump(new_dic,f,indent=4)
			
print('time used: ', time.time() - start)