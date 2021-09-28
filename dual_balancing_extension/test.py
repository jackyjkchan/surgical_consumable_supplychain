from scm_optimization.heuristic_models import LA_DB_Model
from random import random
from scm_optimization.model import *
from scipy.optimize import minimize, bisect, minimize_scalar
from dual_balancing_extension.simulation import Hospital_LA_MDP, Hospital_DB_MDP
import pandas as pd
import pickle
import sys
import os
from multiprocessing import Pool

time.time()


if __name__ == "__main__":
    start_time = time.time()
    print(sys.argv)

    outdir = sys.argv[1] if len(sys.argv) > 1 else "."
    print(os.cpu_count())

    Pool(os.cpu_count()).map(print, range(100000))

    print("CPU Count:", os.cpu_count())
