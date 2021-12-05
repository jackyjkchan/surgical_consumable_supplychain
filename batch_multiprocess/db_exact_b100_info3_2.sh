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
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 79) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 80) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 81) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 82) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 83) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 84) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 85) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 86) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 87) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 88) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 89) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 90) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 91) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 92) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 93) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 94) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 95) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 96) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 97) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 98) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 99) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 100) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 101) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 102) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 103) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 104) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 105) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 106) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 107) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 108) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 109) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 110) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 111) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 112) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 113) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 114) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 115) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 116) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 117) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 7 -b 100 --info 3 --pools 200 --index 118) &
wait