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
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 119) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 120) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 121) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 122) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 123) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 124) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 125) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 126) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 127) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 128) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 129) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 130) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 131) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 132) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 133) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 134) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 135) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 136) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 137) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 138) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 139) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 140) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 141) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 142) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 143) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 144) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 145) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 146) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 147) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 148) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 149) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 150) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 151) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 152) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 153) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 154) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 155) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 156) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 157) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 8 -b 10 --info 3 --pools 200 --index 158) &
wait