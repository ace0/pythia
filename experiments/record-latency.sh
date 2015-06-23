#!/bin/bash -e

N=10000
LOG=logs/client-latency.$(date +"%Y-%m-%d-%H%M").$N
# LOG=logs/client-latency.$(date -d "today" +"%Y%m%d%H%M").$N

# Run latency tests and record the results.
#bash run-latency-tests.sh $N | tee $LOG
bash run-latency-tests.sh $N > $LOG