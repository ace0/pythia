#!/bin/bash -e
# Measure throughput using distributed autobench

#TEST="FAST"
QUIET="1"
TIMEOUT=30
CLIENTS=(localhost 172.31.10.36)

# Choose test settings.
# NOTE: When setting LOW/HIGH - this must be an integer divisable by the number of CLIENTS
#       or httperf dies with a non-obvious error. :/
if [ "$TEST" = "FAST" ]
then
    # Fast test    
    LOW=2000
    HIGH=2400
    STEP=100
    TIME=30
else
    # Full test
    LOW=2000
    HIGH=2500
    STEP=50
    TIME=60
fi

SERVER=$(cat server.ip)
PORT=4600 # autobenchd port
FMT=csv 

##
# Build the client list string
##
for client in "${CLIENTS[@]}"
do
    CLIENT_LIST="${CLIENT_LIST}$client:$PORT,"
done
# Delete the final comma
CLIENT_LIST=${CLIENT_LIST::-1}

##
# URL list
##
STATIC_URL="/dummy-response.html"
VPRF_URL="/pythia/eval-unb?x=This+is+my+next&t=super%2Bsecret_tweak&w=super_secret%2Bclient-id"
BLS_URL="/pythia/eval-bls?x=Thisisatestmessage&t=thisisatesttweakvalue&w=webserverid"
VPOP_URL="/pythia/eval?x=AxRzcDQgF8-yJOZCvYtkVsMrFpcXXDovK_FZ0n-QX8Wh&t=super%2Bsecret_tweak&w=super_secret%2Bclient-id"

#URLS=("$STATIC_URL" "$VPRF_URL" "$BLS_URL" "$VPOP_URL")
#URLS=("$VPOP_URL")
URLS=($STATIC_URL)
#URLS=("$VPRF_URL" "$BLS_URL" "$VPOP_URL")
#URLS=("$BLS_URL" "$VPOP_URL" "$VPRF_URL" "$STATIC_URL")

# Run httperf
function run-httperf()
{
    url="$1"
    RATE=100
    CONN=10000
    httperf --server $SERVER --uri "$url" --ssl --rate $RATE \
	--num-conn $CONN --num-call 1 --timeout $TIMEOUT \
        --print-request=header --print-reply=header
}

# Run autobench on the specified URL
function run-autobench()
{
    url="$1"
    autobench_admin --clients $CLIENT_LIST --single_host \
	--host1 $SERVER --uri1 "$url" --port1 443 \
	--low_rate $LOW --high_rate $HIGH --rate_step $STEP \
        --const_test_time $TIME --num_call 1 --timeout $TIMEOUT \
	--output_fmt $FMT
}

# Run throughput measurements against each URL
for url in "${URLS[@]}"
do
    echo
    echo "Throughput test for ${url}"
    echo "==================================="

    if [ "$QUIET" = "1" ]; then
	run-autobench "$url" 2>/dev/null
    else
	run-autobench "$url" 
    fi
done
