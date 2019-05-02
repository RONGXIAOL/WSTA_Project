import os
# rootdir = os.getcwd()  #获取当前目录
# print(rootdir)
dic = {}
dir_path = '../WSTA_Project_materials/wiki-pages-text/'
list = os.listdir(dir_path)   #列出文件夹下所有的目录与文件
for i in range(0, len(list)):
	file_path = dir_path + list[i]
	with open(file_path,'r', encoding='utf-8') as f:
		lines = f.readlines()
		for line in lines[:3]:
			tokens = line.split()
			doc = tokens[0]
			page = tokens[1]
			text = tokens[2:]
			if doc in dic:
				dic[doc][page] = text
			else:
				dic[doc] = {}
				dic[doc][page] = text
		# print(dic)
print('end')
