import json
from collections import Counter

with open("./data/testset.json", 'r', encoding='utf-8') as f:
	dic = json.load(f)
f2 = open("./myModel/myModel_test_result.tsv", 'r', encoding='utf-8')

num = 0

for _id in dic:
	vote = Counter()
	for i in range(len(dic[_id]["sents"])):
		line = f2.readline()
		probs = [float(prob) for prob in line.split()]
		max_index = probs.index(max(probs))
		if max_index == 0:
			vote["SUPPORTS"] += 1
		elif max_index == 1:
			vote["REFUTES"] += 1
		else:
			vote["NOT ENOUGH INFO"] += 1
	if not vote:
		label = "NOT ENOUGH INFO"
	else:
		if vote["SUPPORTS"] > vote["REFUTES"]:
			label = "SUPPORTS"
		elif vote["SUPPORTS"] < vote["REFUTES"]:
			label = "REFUTES"
		elif vote["SUPPORTS"] == vote["REFUTES"] and vote["SUPPORTS"] > 0:
			label = "SUPPORTS"
		else:
			label = "NOT ENOUGH INFO"
	dic[_id]["label"] = label

with open("./testoutput.json", 'w', encoding='utf-8') as f:
	json.dump(dic,f,indent=4)
