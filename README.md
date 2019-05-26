COMP90042WSTA Project AutomaticFactVerification
======
Team member: Jiazhen Hu, Rongxiao Liu
------

## Requirements
* `python3.6`
* `wget`
* `tensorflow` >= 1.11.0

## Usage:
<b>(1) information extraction</b>  
  
<b>(2) claim verification</b>  
run `run_retrain.sh` in `bert` directory
(add `--use_tpu=True --tpu_name=$TPU_NAME` at the end of command `python3 run_classifier.py` if you have a TPU)
