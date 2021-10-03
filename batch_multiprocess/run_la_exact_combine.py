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
    parser.add_argument('--info', dest='info', type=int, help='info horizon')
    parser.add_argument('--binom_usage_n', dest='binom_usage_n', type=int, help='binom_usage_n')
    parser.add_argument('--pools', dest='pools', type=int, help='num of parallel runners')
    parser.add_argument('--index', dest='pool_num', type=int, help='index of runner, 0 to pools - 1')
    args = parser.parse_args()

    print(args.backlogging_cost)

    outdir = args.outdir if args.outdir else "."
    backlogging_cost = args.backlogging_cost if args.backlogging_cost else 1000
    info = args.info if args.info else 0
    binom_usage_n = args.binom_usage_n if args.binom_usage_n else 0
    pools = args.pools if args.pools else 2
    pool_num = args.pool_num if args.pool_num else 0

    usage_model = BinomUsageModel(n=binom_usage_n, p=1 / binom_usage_n) if binom_usage_n else PoissonUsageModel(scale=1,
                                                                                                                trunk=1e-3)

    info_state_rvs = [pacal.ConstDistr(0)] * info + \
                     [pacal.BinomialDistr(10, 0.5)]
    if info == 0:
        info_state_rvs = [pacal.BinomialDistr(10, 0.5), pacal.ConstDistr(0)]

    gamma = 1
    lead_time = 0
    holding_cost = 1
    setup_cost = 0
    unit_price = 0

    model = LA_DB_Model(gamma,
                        lead_time,
                        info_state_rvs,
                        holding_cost,
                        backlogging_cost,
                        setup_cost,
                        unit_price,
                        usage_model=usage_model)

    prefix = "LA_Model_b_{}_info_{}".format(backlogging_cost, info)
    prefix += "binomial_usage_{}".format(binom_usage_n) if binom_usage_n else ""
    fn = outdir + '/' + prefix
    if os.path.isfile(fn):
        model = LA_DB_Model.read_pickle(fn + "_model.pickle")
    else:
        model.to_pickle(fn)
    print("Writing initial model: ", fn)

    for t in range(21):
        segments = list(fn + "_t_{}_seg_{}_model.pickle".format(t, pool_num) for pool_num in range(pools))
        loading = True
        while loading:
            if all(os.path.isfile(segment) for segment in segments):
                sub_models = list(LA_DB_Model.read_pickle(segment) for segment in segments)
                loading = False
                print("Segments all loaded...")
            else:
                time.sleep(10)

        for sub_model in sub_models:
            model.value_function_j.update(sub_model.value_function_j)
            model.value_function_v.update(sub_model.value_function_v)
            model.order_la_cache.update(sub_model.order_la_cache)
            model.reward_funcion_g_cache.update(sub_model.reward_funcion_g_cache)
            model.demand_rv_cache.update(sub_model.demand_rv_cache)

        prefix_t = prefix + "_t_{}".format(t)
        print("Writing model: ", prefix_t)
        model.to_pickle(outdir + '/' + prefix_t)
        model.to_pickle(fn)
