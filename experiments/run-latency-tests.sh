#!/bin/bash -e

# Number of iterations
N=${1:-1000}

# Django development server URL
DEV_SERVER="http://localhost:8000"

# Try to read the server name from a file
if [ -e server ]
then
    SERVER=$(cat server)
fi

# If there's no server name specified, use the DEV_SERVER as the default
SERVER=${SERVER:-$DEV_SERVER}

# Build the URL
URL=$SERVER/pythia

# Run all test options for a given service
function runAll()
{
    SERVICE=$1
    echo $SERVICE
    echo =======================================
    python clientlatency.py $N $URL $SERVICE --cold
    echo
    python clientlatency.py $N $URL $SERVICE
    echo
    python clientlatency.py $N $URL $SERVICE --noproof
    echo
    echo
    echo
}

# Run the latency tests
runAll vpop 
runAll vprf 
runAll bls 
