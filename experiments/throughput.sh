#!/bin/bash
# Measure throughput using distributed autobench

SERVER=$(cat server.ip)

# Full test
LOW=100
HIGH=1000
STEP=50
TIME=60
CLIENTS="localhost:4600,172.31.0.54:4600,172.31.0.55:4600"

# Fast test
LOW=400
HIGH=1500
STEP=100
TIME=30
CLIENTS="localhost:4600"

STATIC_URL="/index.html"

#EC_URL="/pythia/query-ecc?w=ksENYiseNHMWYLFEiasPb1Ic2b8CdJZqO2xiCBXFTnk=&t=SjjZwHYwrNlGgE7A9Iu5Y90na_d56paKdgTJSPhfzS0=&m=CalPx0KNd53LLsvNEkSjeiLCeGkt_y2FpVaPO_hN-Wg="

#BLS_URL="/pythia/query-bls?w=ksENYiseNHMWYLFEiasPb1Ic2b8CdJZqO2xiCBXFTnk=&t=SjjZwHYwrNlGgE7A9Iu5Y90na_d56paKdgTJSPhfzS0=&m=CalPx0KNd53LLsvNEkSjeiLCeGkt_y2FpVaPO_hN-Wg="

#OBLS_URL="/pythia/oquery-bls?w=ksENYiseNHMWYLFEiasPb1Ic2b8CdJZqO2xiCBXFTnk=&t=SjjZwHYwrNlGgE7A9Iu5Y90na_d56paKdgTJSPhfzS0=&m=2:ijH1B_8W13fmejcGCi-R5EBh3Q0q-sY3jk1M7Y1VXdFJ_iTC_hnDF1IRFTHIAkMNqlHrDj6jYIk37SGsqrtCsaHA49qlQ_x5xZpfvtMyoSK64j8mBkkKpJUtQ6U55pA4zWIiVjRJed4Th4ARmAB96BgubNwJwit8zCBzxAXC5vD__9NXoEfhdn_yYyIRVolxqSr0jt2q5byr-9ApI9OzMto_VcCbgGSk"

URLS=("$EC_URL" "$BLS_URL" "$OBLS_URL")
URLS=($STATIC_URL)

TIMEOUT=5
CLIENT2=localhost
CPORT=4600
FMT=csv
#FMT=tsv

function run-autobench()
{
    url="$1"
    autobench_admin --clients $CLIENTS --quiet --single_host \
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


# Running httperf
#RATE=600
#CONN=36000
#httperf --server $SERVER --uri "$URL" --ssl --rate $RATE \
#    --num-conn $CONN --num-call 1 --timeout $TIMEOUT