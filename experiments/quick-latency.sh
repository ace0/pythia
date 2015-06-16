N=100
SERVER="http://localhost:8000"
URL=$SERVER/pythia/eval

python clientlatency.py $N $URL
echo
python clientlatency.py $N $URL --cold
