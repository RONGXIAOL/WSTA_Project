# import allennlp
# from allennlp.predictors.predictor import Predictor
# from allennlp.models.archival import load_archive
# model_path = "https://s3-us-west-2.amazonaws.com/allennlp/models/ner-model-2018.12.18.tar.gz"
# model_path = "D:\\Documents\\WSTA\\Project\\model\\ner"
# archive = load_archive(model_path, cuda_device=0)
# predictor = Predictor.from_archive(archive)
# sys.exit(0)

# def get_allen_entitys(tags, words):
#     line = {"sentence" : claim}
#     r = predictor.predict_json(line)
#     tags = r['tags']
#     words = r['words']
#     claim_entitys[key] = get_entitys(tags, words)
#     entitys = []
#     curr_entity = None
#     curr_label = None
#     for ij in range(len(tags)):
#         tag = tags[ij]
#         if(len(tag) > 1):
#             info = tag.split('-')
#             label_type = info[1]
#             label_pos = info[0]
#             word = words[ij]
#             if (label_pos == 'U'):
#                 curr_entity = word
#                 curr_label = label_type
#                 # print(label_pos, curr_entity, curr_label)
#                 entitys.append([curr_entity, curr_label])
#                 curr_entity = None
#                 curr_label = None
#                 continue
#             elif (label_pos == 'B'):
#                 curr_entity = word
#                 curr_label = label_type
#                 # print(label_pos, curr_entity, curr_label)
#                 continue
#             elif (label_pos == 'I'):
#                 curr_entity = curr_entity + ' ' + word
#                 # print(label_pos, curr_entity, curr_label)
#                 continue
#             elif (label_pos == 'L'):
#                 curr_entity = curr_entity + ' ' + word
#                 # print(label_pos, curr_entity, curr_label)
#                 entitys.append([curr_entity, curr_label])
#                 curr_entity = None
#                 curr_label = None
#                 continue
#             else:
#                 sys.exit(-1)
#     return entitys
