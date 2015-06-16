N=100
SERVER="http://localhost:8000"
URL=$SERVER/pythia/eval

echo python clientlatency.py $N $URL
python clientlatency.py $N $URL
