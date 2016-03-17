Usage Memo
==========

tea
---

export DATA_PATH=data/d3_20151201-20160201.tsv

export MODEL_NAME=tea
export MODEL_PATH=model/${MODEL_NAME}
export SAMPLE_OUT=${MODEL_NAME}.json

PYTHONPATH=src python src/event_simulator/script/train.py --data "$DATA_PATH" --model "$MODEL_PATH" --num_step 10 --batch_size 500 --epoch 20 --sep_tab
PYTHONPATH=src python src/event_simulator/script/generate.py --model "$MODEL_PATH" --output "$SAMPLE_OUT" --num_sample 10000
PYTHONPATH=src python src/event_simulator/script/evaluate.py --data "$DATA_PATH" --sample "$SAMPLE_OUT"

### ex2)

grep -v activities.pageview data/d3_20151201-20160201.tsv > data/d3_20151201-20160201_exclude_page_view.tsv

export DATA_PATH=data/d3_20151201-20160201_exclude_page_view.tsv
export MODEL_NAME=tea2
export MODEL_PATH=model/${MODEL_NAME}
export SAMPLE_OUT=${MODEL_NAME}.json


PYTHONPATH=src python src/event_simulator/script/train.py --data "$DATA_PATH" --model "$MODEL_PATH" --hidden_size 30 --num_step 10 --batch_size 500 --epoch 20 
PYTHONPATH=src python src/event_simulator/script/generate.py --model "$MODEL_PATH" --output "$SAMPLE_OUT" --num_sample 10000
PYTHONPATH=src python src/event_simulator/script/evaluate.py --data "$DATA_PATH" --sample "$SAMPLE_OUT"


### ex3)

grep -v view_product_detail data/d3_20151201-20160201_exclude_page_view.tsv > data/d3_20151201-20160201_exclude_page_view_and_view_product_detail.tsv
export DATA_PATH=data/d3_20151201-20160201_exclude_page_view_and_view_product_detail.tsv
export MODEL_NAME=tea3
export MODEL_PATH=model/${MODEL_NAME}
export SAMPLE_OUT=${MODEL_NAME}.json
 
PYTHONPATH=src python src/event_simulator/script/train.py --data "$DATA_PATH" --model "$MODEL_PATH" --hidden_size 30 --num_step 10 --batch_size 500 --epoch 20 
PYTHONPATH=src python src/event_simulator/script/generate.py --model "$MODEL_PATH" --output "$SAMPLE_OUT" --num_sample 10000
PYTHONPATH=src python src/event_simulator/script/evaluate.py --data "$DATA_PATH" --sample "$SAMPLE_OUT"

-> 悪くなった

### ex4)

packaging に prepend をつけた

cp data/d3_20151201-20160201_exclude_page_view.tsv data/d3_20151201-20160201_exclude_page_view-2.tsv

export DATA_PATH=data/d3_20151201-20160201_exclude_page_view-2.tsv
export MODEL_NAME=tea4
export MODEL_PATH=model/${MODEL_NAME}
export SAMPLE_OUT=${MODEL_NAME}.json


PYTHONPATH=src python src/event_simulator/script/train.py --data "$DATA_PATH" --model "$MODEL_PATH" --hidden_size 30 --num_step 10 --batch_size 500 --epoch 20 
PYTHONPATH=src python src/event_simulator/script/generate.py --model "$MODEL_PATH" --output "$SAMPLE_OUT" --num_sample 10000
PYTHONPATH=src python src/event_simulator/script/evaluate.py --data "$DATA_PATH" --sample "$SAMPLE_OUT"


### ex5)

packaging の時にShuffleするようにした

cp data/d3_20151201-20160201_exclude_page_view.tsv data/d3_20151201-20160201_exclude_page_view-3.tsv

export DATA_PATH=data/d3_20151201-20160201_exclude_page_view-3.tsv
export MODEL_NAME=tea5
export MODEL_PATH=model/${MODEL_NAME}
export SAMPLE_OUT=${MODEL_NAME}.json


PYTHONPATH=src python src/event_simulator/script/train.py --data "$DATA_PATH" --model "$MODEL_PATH" --hidden_size 30 --num_step 10 --batch_size 500 --epoch 20 
PYTHONPATH=src python src/event_simulator/script/generate.py --model "$MODEL_PATH" --output "$SAMPLE_OUT" --num_sample 10000
PYTHONPATH=src python src/event_simulator/script/evaluate.py --data "$DATA_PATH" --sample "$SAMPLE_OUT"

### ex6)

hidden_size=20, layers=3 にしてみる

export DATA_PATH=data/d3_20151201-20160201_exclude_page_view-3.tsv
export MODEL_NAME=tea6
export MODEL_PATH=model/${MODEL_NAME}
export SAMPLE_OUT=${MODEL_NAME}.json


PYTHONPATH=src python src/event_simulator/script/train.py --data "$DATA_PATH" --model "$MODEL_PATH" --num_layers 3 --hidden_size 20 --num_step 10 --batch_size 500 --epoch 20 
PYTHONPATH=src python src/event_simulator/script/generate.py --model "$MODEL_PATH" --output "$SAMPLE_OUT" --num_sample 10000
PYTHONPATH=src python src/event_simulator/script/evaluate.py --data "$DATA_PATH" --sample "$SAMPLE_OUT"

### ex7)

hidden_size=40, layers=1 にしてみる

export DATA_PATH=data/d3_20151201-20160201_exclude_page_view-3.tsv
export MODEL_NAME=tea7
export MODEL_PATH=model/${MODEL_NAME}
export SAMPLE_OUT=${MODEL_NAME}.json


PYTHONPATH=src python src/event_simulator/script/train.py --data "$DATA_PATH" --model "$MODEL_PATH" --num_layers 1 --hidden_size 40 --num_step 10 --batch_size 500 --epoch 20 
PYTHONPATH=src python src/event_simulator/script/generate.py --model "$MODEL_PATH" --output "$SAMPLE_OUT" --num_sample 10000
PYTHONPATH=src python src/event_simulator/script/evaluate.py --data "$DATA_PATH" --sample "$SAMPLE_OUT"

