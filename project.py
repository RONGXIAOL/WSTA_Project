import json
import os
from collections import Counter

dir_path = '../WSTA_Project_materials/wiki-pages-text/'
train_path = '../WSTA_Project_materials/train.json'

def parse_wiki(path):
	dic = {}
	file_list = os.listdir(path)   #列出文件夹下所有的目录与文件
	for i in range(0, len(file_list)):
		file_path = path + file_list[i]
		with open(file_path,'r', encoding='utf-8') as text_file:
			lines = text_file.readlines()
			for line in lines:
				tokens = line.split()
				doc = tokens[0]
				sent = tokens[1]
				text = tokens[2:]
				if doc in dic:
					dic[doc][sent] = text
				else:
					dic[doc] = {}
					dic[doc][sent] = text
			
	print('end')
	print(dic)
	return dic
	
def parse_train(path,dic):
	with open(path,'r',encoding='utf-8') as train_file:
		train_set = json.load(train_file)
		for _id in train_set:
			try:
				claim = train_set[_id]['claim']
				evidences = [dic[evidence[0]][str(evidence[1])] for evidence in train_set[_id]['evidence']]

				label = train_set[_id]['label']
				print(claim)
				print(evidences)
				print(label)
				print()
			except Exception as e:
				print(e)

def get_freq(dic):
	doc_term_freq = {}
	term_doc_freq = Counter()
	for doc in dic:
		counter = Counter()
		for sent in dic[doc]:
			counter += Counter(dic[doc][sent])
		doc_term_freq[doc] = counter
		term_doc_freq += Counter([word for word in counter])
	return [doc_term_freq,term_doc_freq]

# parse_wiki(dir_path)
dic = parse_wiki(dir_path)
parse_train(train_path,dic)
print('end')
