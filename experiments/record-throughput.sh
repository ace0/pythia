#!/bin/bash -e

LOG=logs/throughput.$(date +"%Y-%m-%d-%H%M")
./throughput.sh 2>&1  > $LOG
