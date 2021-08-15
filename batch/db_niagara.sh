#!/bin/bash
#SBATCH --time=12:00:00
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:/home/s/sarhangi/jachan/surgical_consumable_supplychain"
./venv/bin/python dual_balancing_extension/run_db_sim_args.py $SCRATCH
