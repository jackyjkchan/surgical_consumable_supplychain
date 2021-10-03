from scm_optimization.heuristic_models import LA_DB_Model
from multiprocessing import Pool
from random import random
from scm_optimization.model import *
from scipy.optimize import minimize, bisect, minimize_scalar
from dual_balancing_extension.simulation import Hospital_LA_MDP, Hospital_DB_MDP
import pandas as pd
import pickle
import sys
import random
import argparse

time.time()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run LA Experiment parallel runners.')
    parser.add_argument('--outdir', dest='outdir', help='output dir to write in')
    parser.add_argument('-b', dest='backlogging_cost', type=int, help='backlogging cost')
    parser.add_argument('--info', dest='info',  type=int, help='info horizon')
    parser.add_argument('--binom_usage_n', dest='binom_usage_n', type=int, help='binom_usage_n')
    parser.add_argument('--pools', dest='pools', type=int, help='num of parallel runners')
    parser.add_argument('--index', dest='pool_num', type=int, help='index of runner, 0 to pools - 1')
    parser.add_argument('-t', dest='t', type=int, help='starting time step')

    args = parser.parse_args()

    print(args.backlogging_cost)

    outdir = args.outdir if args.outdir else "."
    backlogging_cost = args.backlogging_cost if args.backlogging_cost else 1000
    info = args.info if args.info else 0
    binom_usage_n = args.binom_usage_n if args.binom_usage_n else 0
    pools = args.pools if args.pools else 2
    pool_num = args.pool_num if args.pool_num else 0
    t = args.t if args.t else 0

    prefix = "LA_Model_b_{}_info_{}".format(backlogging_cost, info)
    prefix += "binomial_usage_{}".format(binom_usage_n) if binom_usage_n else ""
    fn = outdir + '/' + prefix
    model = None

    for t in range(t, 21):
        if t:
            fn_t = fn + "_t_{}".format(t-1) + "_model.pickle"
        else:
            fn_t = fn + "_model.pickle"

        loading = True
        while loading:
            if os.path.isfile(fn_t):
                print("Model found, loading...")
                time.sleep(5)
                model = LA_DB_Model.read_pickle(fn_t)
                loading = False
            else:
                time.sleep(10)

        all_info_states = list(o for o in model.info_states())
        all_info_states.sort()
        info_states = all_info_states[pool_num::pools]

        for o in info_states:
            for x in range(21):
                model.j_function_la(t, x, o)
                # print("state:", (t, x, o))
                # print("\t", "order:", model.order_la(t, x, o))
                # print("\t", "j_func:", model.j_function_la(t, x, o))

        fn_seg = fn + "_t_{}_seg_{}".format(t, pool_num)
        model.to_pickle(fn_seg)

