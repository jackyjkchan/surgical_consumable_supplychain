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
(./venv/bin/python batch_multiprocess/run_db_exact_combine.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 0) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 1) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 2) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 3) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 4) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 5) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 6) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 7) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 8) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 9) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 10) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 11) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 12) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 13) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 14) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 15) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 16) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 17) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 18) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 19) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 20) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 21) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 22) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 23) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 24) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 25) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 26) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 27) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 28) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 29) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 30) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 31) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 32) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 33) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 34) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 35) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 36) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 37) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 5 -b 100 --info 3 --pools 159 --index 38) &
wait