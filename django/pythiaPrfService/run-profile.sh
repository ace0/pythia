N=10000
LOG=logs/client-server-profile.$(date +"%Y-%m-%d-%H%M").$N

kernprof -l -v profiler.py $N vprf 2>&1 | tee $LOG.vprf
kernprof -l -v profiler.py $N bls  2>&1 | tee $LOG.bls
kernprof -l -v profiler.py $N vpop 2>&1 | tee $LOG.vpop
