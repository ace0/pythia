#!/bin/bash
set -e

# Number of iterations
N=10000

# Log file
LOG=logs/client-latency.$(date -d "today" +"%Y%m%d%H%M").$N

# Dev server
DEV_SERVER="http://localhost:8000"

# Try to read the server name from a file
if [ -e server ]
then
    SERVER=$(cat server)
fi

SERVER=${SERVER:-DEV_SERVER}

# Build the URL
URL=$SERVER/pythia/eval

# Run the latency tests
python clientlatency.py $N $URL | tee $LOG
echo
python clientlatency.py $N $URL --cold | tee -a $LOG
