import allennlp
import time
import json
import pickle
import sys
from allennlp.predictors.predictor import Predictor
from allennlp.models.archival import load_archive


# model_path = "https://s3-us-west-2.amazonaws.com/allennlp/models/ner-model-2018.12.18.tar.gz"
# predictor = Predictor.from_path(model_path)

model_path = "D:\\Documents\\WSTA\\data\\allennlp.model"
archive = load_archive(model_path, cuda_device=0)
predictor = Predictor.from_archive(archive)

print("model loaded")

with open("D:\\Documents\\WSTA\\data\\train.ner.pickle", 'rb') as train_ner_in:
    start = time.time()
    ners = pickle.load(train_ner_in)
    print("start tuning ners")
    count = 0
    for i in range(len(ners)):
        ner = ners[i]
        claim = ner[0]
        wrong = ner[1]
        if('-' not in claim):
            continue
        
        claim = claim.replace('-', ' ')
        line = {"sentence" : claim}
        r = predictor.predict_json(line)
        tags = r['tags']
        words = r['words']
        
        entity = []
        curr_entity = None
        curr_label = None
        for ij in range(len(tags)):
            tag = tags[ij]
            if(len(tag) > 1):
                info = tag.split('-')
                label_type = info[1]
                label_pos = info[0]
                word = words[ij]
                if (label_pos == 'U'):
                    curr_entity = word
                    curr_label = label_type
                    # print(label_pos, curr_entity, curr_label)
                    entity.append([curr_entity, curr_label])
                    curr_entity = None
                    curr_label = None
                    continue
                elif (label_pos == 'B'):
                    curr_entity = word
                    curr_label = label_type
                    # print(label_pos, curr_entity, curr_label)
                    continue
                elif (label_pos == 'I'):
                    curr_entity = curr_entity + ' ' + word
                    # print(label_pos, curr_entity, curr_label)
                    continue
                elif (label_pos == 'L'):
                    curr_entity = curr_entity + ' ' + word
                    # print(label_pos, curr_entity, curr_label)
                    entity.append([curr_entity, curr_label])
                    curr_entity = None
                    curr_label = None
                    continue
                else:
                    print(info, word)
        
        if(len(wrong) == len(entity)):
            continue
        
        ners[i][1] = entity
        print(i)
        if(i % 1000 == 0):
            now = time.time()
            print(i, (now - start) / 60.0)

with open("D:\\Documents\\WSTA\\data\\ner.pickle", 'wb') as ner_out:
    pickle.dump(ners, ner_out)
    print("ner pickle dumped")