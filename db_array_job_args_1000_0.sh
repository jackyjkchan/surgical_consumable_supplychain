#!/bin/bash
#SBATCH --time=06:00:00
#SBATCH --mem-per-cpu=1G
#SBATCH --array=1-3000
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:/home/jachan/projects/def-sarhangi/jachan/surgical_consumable_supplychain"
./venv/bin/python dual_balancing_extension/run_sim.py $SLURM_ARRAY_TASK_ID 1000 0
