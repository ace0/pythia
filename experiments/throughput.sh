#!/bin/bash -e
# Measure throughput using distributed autobench

SERVER=$(cat server.ip)

# autobenchd port
PORT=4600

# Full test
LOW=100
HIGH=1000
STEP=50
TIME=60


# Fast test
LOW=12000
HIGH=20000
STEP=500
TIME=60
CLIENTS=(localhost 172.31.8.148 172.31.8.149)

STATIC_URL="/index.html"

# Build the client list string
for client in "${CLIENTS[@]}"
do
    CLIENT_LIST="${CLIENT_LIST}$client:$PORT,"
done
# Delete the final comma
CLIENT_LIST=${CLIENT_LIST::-1}
echo $CLIENT_LIST

VPRF_URL="/pythia/eval-unb?x=This+is+my+next&t=super%2Bsecret_tweak&w=super_secret%2Bclient-id"

BLS_URL="pythia/eval-bls?x=This+is+my+next&t=super%2Bsecret_tweak&w=super_secret%2Bclient-id"

VPOP_URL="pythia/eval?x=AxRzcDQgF8-yJOZCvYtkVsMrFpcXXDovK_FZ0n-QX8Wh&t=super%2Bsecret_tweak&w=super_secret%2Bclient-id"

URLS=("$STATIC_URL" "$EC_URL" "$BLS_URL" "$OBLS_URL")
URLS=($STATIC_URL)

TIMEOUT=5
CLIENT2=localhost
CPORT=4600
FMT=csv 

# Run httperf
function run-httperf()
{
    RATE=600
    CONN=36000
    httperf --server $SERVER --uri "$URL" --ssl --rate $RATE \
	--num-conn $CONN --num-call 1 --timeout $TIMEOUT
}

# Run autobench on the specified URL
function run-autobench()
{
    url="$1"
    autobench_admin --clients $CLIENT_LIST --quiet --single_host \
	--host1 $SERVER --uri1 "$url" --port1 443 \
	--low_rate $LOW --high_rate $HIGH --rate_step $STEP \
        --const_test_time $TIME --num_call 1 --timeout $TIMEOUT \
	--output_fmt $FMT \
	2> /dev/null
}

# Run throughput measurements against each URL
for url in "${URLS[@]}"
do
    echo
    echo "Throughput test for ${url}"
    echo
    run-autobench "$url" 
done
