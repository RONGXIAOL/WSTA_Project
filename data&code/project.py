import os
rootdir = os.getcwd()  #获取当前目录
print(rootdir)
list =os.listdir('../../WSTA_Project_materials/wiki-pages-text') #列出文件夹下所有的目录与文件
for i in range(0,len(list)):
    print(list[i])

