wget https://storage.googleapis.com/bert_models/2018_10_18/cased_L-12_H-768_A-12.zip
unzip cased_L-12_H-768_A-12.zip
python3 ../bert/run_classifier.py \
  --task_name=mypr \
  --do_train=true \
  --do_eval=true \
  --do_predict=true \
  --data_dir=../data \
  --vocab_file=./cased_L-12_H-768_A-12/vocab.txt \
  --bert_config_file=./cased_L-12_H-768_A-12/bert_config.json \
  --init_checkpoint=./cased_L-12_H-768_A-12/bert_model.ckpt \
  --do_lower_case=False \
  --max_seq_length=128 \
  --train_batch_size=32 \
  --learning_rate=2e-5 \
  --num_train_epochs=3.0 \
  --output_dir=./mymodel
python3 label_generator.py