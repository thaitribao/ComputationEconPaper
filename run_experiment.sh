#!/bin/bash

RESULT_ERS=result_ers.csv
RESULT_SRS=result_srs.csv 

RESULT_ERS_ENDO=result_ers_endo.csv 
RESULT_SRS_ENDO=result_srs_endo.csv 

RESULT_ERS_STARS=result_ers_stars.csv 
RESULT_SRS_STARS=result_srs_stars.csv

GRAPH_OUTPUT_BASELINE=baseline.png
GRAPH_OUTPUT_ENDO=endo.png
GRAPH_OUTPUT_STARS=stars.png

NUM_PERIOD=500
NUM_SEEDS=100

echo "Running baseline with ERS"
python bhole_hanna.py --type ERS --num_period $NUM_PERIOD --num_seed $NUM_SEEDS --output $RESULT_ERS --endogenous False --star_rating False 

echo "Running baseline with SRS"
python bhole_hanna.py --type SRS --num_period $NUM_PERIOD --num_seed $NUM_SEEDS --output $RESULT_SRS --endogenous False --star_rating False

echo "Running Endogenous switching with ERS"
python bhole_hanna.py --type ERS --num_period $NUM_PERIOD --num_seed $NUM_SEEDS --output $RESULT_ERS_ENDO --endogenous True --star_rating False

echo "Running Endogenous switching with SRS"
python bhole_hanna.py --type SRS --num_period $NUM_PERIOD --num_seed $NUM_SEEDS --output $RESULT_SRS_ENDO --endogenous True --star_rating False 

echo "Running subjective Endogenous switching with ERS"
python bhole_hanna.py --type ERS --num_period $NUM_PERIOD --num_seed $NUM_SEEDS --output $RESULT_ERS_ENDO --endogenous True --star_rating True

echo "Running subjective Endogenous switching with SRS"
python bhole_hanna.py --type SRS --num_period $NUM_PERIOD --num_seed $NUM_SEEDS --output $RESULT_SRS_ENDO --endogenous True --star_rating True

echo "Plotting results" 
python plot_result.py --num_seed $NUM_SEEDS --num_period $NUM_PERIOD --ERS $RESULT_ERS --SRS $RESULT_SRS --output $GRAPH_OUTPUT
python plot_result.py --num_seed $NUM_SEEDS --num_period $NUM_PERIOD --ERS $RESULT_ERS_ENDO --SRS $RESULT_SRS_ENDO --output $GRAPH_OUTPUT_ENDO
python plot_result.py --num_seed $NUM_SEEDS --num_period $NUM_PERIOD --ERS $RESULT_ERS_STARS --SRS $RESULT_SRS_STARS --output $GRAPH_OUTPUT_STARS



