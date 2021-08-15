#!/bin/bash
# SLURM submission script for multiple serial jobs on Niagara
#
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=40
#SBATCH --time=48:00:00
#SBATCH --job-name serialx40

# Turn off implicit threading in Python, R
export OMP_NUM_THREADS=1
cd /home/s/sarhangi/jachan/surgical_consumable_supplychain
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:/home/s/sarhangi/jachan/surgical_consumable_supplychain"

# EXECUTION COMMAND; ampersand off 40 jobs and wait
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
(./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH) &
wait