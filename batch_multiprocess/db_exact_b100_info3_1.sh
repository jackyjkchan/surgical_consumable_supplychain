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
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 39) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 40) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 41) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 42) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 43) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 44) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 45) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 46) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 47) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 48) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 49) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 50) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 51) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 52) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 53) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 54) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 55) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 56) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 57) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 58) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 59) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 60) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 61) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 62) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 63) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 64) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 65) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 66) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 67) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 68) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 69) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 70) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 71) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 72) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 73) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 74) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 75) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 76) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 77) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 14 -b 100 --info 3 --pools 200 --index 78) &
wait