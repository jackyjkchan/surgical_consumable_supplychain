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
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 159) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 160) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 161) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 162) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 163) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 164) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 165) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 166) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 167) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 168) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 169) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 170) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 171) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 172) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 173) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 174) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 175) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 176) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 177) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 178) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 179) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 180) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 181) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 182) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 183) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 184) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 185) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 186) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 187) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 188) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 189) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 190) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 191) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 192) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 193) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 194) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 195) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 196) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 197) &
(./venv/bin/python batch_multiprocess/run_db_exact_segment.py --outdir $SCRATCH -t 17 -b 100 --info 3 --pools 200 --index 198) &
wait