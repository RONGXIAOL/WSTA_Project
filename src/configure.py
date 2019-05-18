import os

ROOTPATH = os.getcwd() + "\\"
DATAPATH = ROOTPATH + "data\\"
JSONPATH = DATAPATH + "json\\"
PICKPATH = DATAPATH + "pick\\"
SORTPATH = DATAPATH + "sort\\"
DUMPPATH = DATAPATH + "dump\\"
# WIKIPATH = DATAPATH + "wiki\\"

TRN_JSON = JSONPATH + "train.json"
DEV_JSON = JSONPATH + "devset.json"
TST_JSON = JSONPATH + "test-unlabelled.json"

DEV_ANSW = JSONPATH + "devoutput.json"
TST_ANSW = JSONPATH + "testoutput.json"
DEV_DOCS = JSONPATH + "dev_docs.json"
TST_DOCS = JSONPATH + "test_docs.json"

TRN_NERS = JSONPATH + "train_entitys.json"
DEV_NERS = JSONPATH + "dev_entitys.json"
TST_NERS = JSONPATH + "test_entitys.json"

CAP_JSON = JSONPATH + "capital.json"
TPC_PICK = PICKPATH + "topics.pickle"
TRM_PICK = PICKPATH + "trimed.pickle"
INT_PICK = PICKPATH + "interval.pickle"
DWK_PICK = PICKPATH + "doc_wiki.pickle"

DUMPLIST = os.listdir(DUMPPATH)
# WIKILIST = os.listdir(WIKIPATH)

TRN_STEP = 10000
TST_STEP = 1000
CUT_SIZE = 230000
LEN_DIFF = 2
TOP_THRE = 5
