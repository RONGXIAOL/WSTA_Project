import os

ROOTPATH = os.getcwd() + "\\"
DATAPATH = ROOTPATH + "data\\"
JSONPATH = DATAPATH + "json\\"
PICKPATH = DATAPATH + "pick\\"
SORTPATH = DATAPATH + "sort\\"
DUMPPATH = DATAPATH + "dump\\"
INSPPATH = DATAPATH + "insp\\"
WIKIPATH = DATAPATH + "wiki\\"

DEV_JSON = JSONPATH + "dev_set.json"
TST_JSON = JSONPATH + "test_set.json"
TRN_JSON = JSONPATH + "train_set.json"
SUP_JSON = JSONPATH + 'sup_set.json'
REF_JSON = JSONPATH + 'ref_set.json'
NEI_JSON = JSONPATH + 'nei_set.json'

DEV_ANSW = JSONPATH + "devoutput.json"
TST_ANSW = JSONPATH + "testoutput.json"
TRN_ANSW = JSONPATH + "trainoutput.json"
SUP_ANSW = JSONPATH + 'supoutput.json'
REF_ANSW = JSONPATH + 'refoutput.json'
NEI_ANSW = JSONPATH + 'neioutput.json'

DEV_DOCS = JSONPATH + "dev_docs.json"
TST_DOCS = JSONPATH + "test_docs.json"
TRN_DOCS = JSONPATH + "train_docs.json"
SUP_DOCS = JSONPATH + 'sup_docs.json'
REF_DOCS = JSONPATH + 'ref_docs.json'
NEI_DOCS = JSONPATH + 'nei_docs.json'

DEV_NERS = JSONPATH + "dev_entitys.json"
TST_NERS = JSONPATH + "test_entitys.json"
TRN_NERS = JSONPATH + "train_entitys.json"
SUP_NERS = JSONPATH + 'sup_entitys.json'
REF_NERS = JSONPATH + 'ref_entitys.json'
NEI_NERS = JSONPATH + 'nei_entitys.json'

CAP_JSON = JSONPATH + "capital.json"
TPC_PICK = PICKPATH + "topics.pickle"
TRM_PICK = PICKPATH + "trimed.pickle"
INT_PICK = PICKPATH + "interval.pickle"
DWK_PICK = PICKPATH + "doc_wiki.pickle"

DEV_MODE = 1
TST_MODE = 2
TRN_MODE = 3
SUP_MODE = 4
REF_MODE = 5
NEI_MODE = 6

DUMPLIST = os.listdir(DUMPPATH)
WIKILIST = os.listdir(WIKIPATH)

CUT_SIZE = 230000
DIF_SIZE = 2

SIM_THRE = 0.4
TOP_THRE = 5
