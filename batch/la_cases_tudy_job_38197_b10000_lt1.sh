#!/bin/bash
#SBATCH --time=12:00:00
#SBATCH --mem-per-cpu=1G
#SBATCH --array=0-499
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:/home/jachan/projects/def-sarhangi/jachan/surgical_consumable_supplychain"
./venv/bin/python dual_balancing_extension/run_la_case_study.py $SLURM_ARRAY_TASK_ID 38197 10000 -1 1
