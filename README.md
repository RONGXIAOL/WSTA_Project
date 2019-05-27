COMP90042WSTA Project AutomaticFactVerification
======
Team member: Jiazhen Hu(971800), Rongxiao Liu(927694)
------

## Requirements
* `python3.6`
* `wget`
* `tensorflow` >= 1.11.0

## Path and files
Before running the code, make sure you have a 'data' folder under project root folder       
and make sure your data folder looks like this
```
    $ tree data
    data
    ├─dump
    ├─insp
    ├─json
    ├───── devset.json
    ├───── test-unlabelled.json
    ├───── train.json
    ├─pick
    ├─sort
    ├─wiki
    ├───── wiki-001.txt
    ├───── .
    ├───── .
    ├───── .
    ├───── wiki-109.txt
```

## Usage:
<b>(1) information extraction</b>  
In project root directory,  
run dev set with command `python3 src/app.py dev`  
run test set with command `python3 src/app.py test`  
run train set with command `python3 src/app.py train`  
<b>(2) claim verification</b>  
run `run_retrain.sh` in `bert` directory  
(add `--use_tpu=True --tpu_name=$TPU_NAME` at the end of command `python3 run_classifier.py` if you have a TPU)


## Reference
* The directory `bert` is cloned from https://github.com/google-research/bert.git with modification on `run_classifier.py`.
* The pretrained bert model is downloaded from https://storage.googleapis.com/bert_models/2018_10_18/cased_L-12_H-768_A-12.zip

