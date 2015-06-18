#!/bin/bash
set -e

# Number of iterations
N=100

# Dev server
DEV_SERVER="http://localhost:8000"

# Try to read the server name from a file
if [ -e server ]
then
    SERVER=$(cat server)
fi

SERVER=${SERVER:-$DEV_SERVER}

# Build the URL
URL=$SERVER/pythia

# Run hot and cold tests for a given service
function runBoth()
{
    SERVICE=$1
    python clientlatency.py $N $URL $SERVICE
    echo
    python clientlatency.py $N $URL $SERVICE --cold
    echo
    echo
}

# Run the latency tests
runBoth vpop
runBoth vprf
runBoth bls