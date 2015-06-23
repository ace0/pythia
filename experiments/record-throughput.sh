#!/bin/bash -e

LOG=logs/throughput.$(date +"%Y-%m-%d-%H%M")
bash throughput.sh  > $LOG