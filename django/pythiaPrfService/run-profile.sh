N=1000
FILE=logs/component-server-us-west
DATE=`date --iso-8601=seconds`

kernprof -l -v profiler.py $N "query-ecc"  | tee $FILE-query-ecc-$DATE
kernprof -l -v profiler.py $N "query-bls"  | tee $FILE-query-bls-$DATE
kernprof -l -v profiler.py $N "oquery-bls" | tee $FILE-oquery-bls-$DATE
