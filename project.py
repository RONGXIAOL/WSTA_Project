import json
import os

dir_path = '../WSTA_Project_materials/wiki-pages-text/'
train_path = '../WSTA_Project_materials/train.json'

def parse_wiki(path):
	dic = {}
	list = os.listdir(path)   #列出文件夹下所有的目录与文件
	for i in range(0, len(list)):
		file_path = path + list[i]
		with open(file_path,'r', encoding='utf-8') as text_file:
			lines = text_file.readlines()
			for line in lines[:3]:
				tokens = line.split()
				doc = tokens[0]
				sent = tokens[1]
				text = tokens[2:]
				if doc in dic:
					dic[doc][sent] = text
				else:
					dic[doc] = {}
					dic[doc][sent] = text
			# print(dic)
	print('end')
	return dic
	

def parse_train(path):
	with open(path,'r',encoding='utf-8') as train_file:
		train_set = json.load(train_file)
		# print(train_set)
		for _id in train_file:
			claim = train_file[_id]['claim']
			# evid_doc, evid_sent = train_file[_id]['evidence']
			# evidence = dic[evid_doc][evid_sent]
			# label = train_file[_id]['label']
			print(claim)
			# print(evidence)
			print(label)

# parse_wiki(dir_path)
parse_train(train_path)
print('end')
