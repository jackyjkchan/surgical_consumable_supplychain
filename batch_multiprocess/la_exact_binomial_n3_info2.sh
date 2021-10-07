#!/bin/bash
# SLURM submission script for multiple serial jobs on Niagara
#
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=40
#SBATCH --time=24:00:00
#SBATCH --job-name serialx40

# Turn off implicit threading in Python, R
export OMP_NUM_THREADS=1
cd /home/s/sarhangi/jachan/surgical_consumable_supplychain
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:/home/s/sarhangi/jachan/surgical_consumable_supplychain"

# EXECUTION COMMAND; ampersand off 40 jobs and wait
(./venv/bin/python batch_multiprocess/run_la_exact_combine.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39 ) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 0) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 1) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 2) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 3) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 4) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 5) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 6) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 7) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 8) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 9) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 10) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 11) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 12) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 13) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 14) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 15) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 16) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 17) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 18) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 19) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 20) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 21) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 22) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 23) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 24) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 25) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 26) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 27) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 28) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 29) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 30) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 31) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 32) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 33) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 34) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 35) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 36) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 37) &
(./venv/bin/python batch_multiprocess/run_la_exact_segment.py --outdir $SCRATCH --binom_usage_n 3 -b 1000 --info 2 --pools 39  --index 38) &
wait