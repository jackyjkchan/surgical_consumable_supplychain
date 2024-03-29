#!/bin/bash
#SBATCH --time=09:30:00
#SBATCH --mem-per-cpu=1G
#SBATCH --array=1-3000
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:/home/jachan/projects/def-sarhangi/jachan/surgical_consumable_supplychain"
./venv/bin/python dual_balancing_extension/run_la_sim_args.py $SLURM_ARRAY_TASK_ID 1000 2 4
