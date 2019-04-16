#!/bin/bash

RESULT_ERS=result_ers.csv
RESULT_SRS=result_srs.csv 
GRAPH_OUTPUT=baseline.png

NUM_PERIOD=500
NUM_SEEDS=100

python bhole_hanna.py --type ERS \
                      --num_period $NUM_PERIOD \
                      --num_seed $NUM_SEEDS \ 
                      --output $RESULT_ERS \
                      --debug False

python bhole_hanna.py --type SRS \ 
                      --num_period $NUM_PERIOD \
                      --num_seed $NUM_SEEDS \ 
                      --output $RESULT_SRS \
                      --debug False 

python plot_result.py --num_seed $NUM_SEEDS \
                      --num_period $NUM_PERIOD \
                      --ERS $RESULT_ERS \ 
                      --SRS $RESULT_SRS \
                      --output $GRAPH_OUTPUT