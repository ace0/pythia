
N=100

# Dev server
SERVER="http://localhost:8000"

# XP server
SERVER="https://localhost"

URL=$SERVER/pythia/eval

python clientlatency.py $N $URL
echo
python clientlatency.py $N $URL --cold
