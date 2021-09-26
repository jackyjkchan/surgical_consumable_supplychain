from scm_optimization.heuristic_models import LA_DB_Model
from random import random
from scm_optimization.model import *
from scipy.optimize import minimize, bisect, minimize_scalar
from dual_balancing_extension.simulation import Hospital_LA_MDP, Hospital_DB_MDP
import pandas as pd
import pickle
import sys

time.time()


if __name__ == "__main__":
    start_time = time.time()
    print(sys.argv)

    outdir = sys.argv[1] if len(sys.argv) > 1 else "."
    backlogging_cost = int(sys.argv[2]) if len(sys.argv) > 1 else 1000
    info = int(sys.argv[3]) if len(sys.argv) > 1 else 0
    binom_usage_n = int(sys.argv[4]) if len(sys.argv) == 5 else 0

    lead_time = 0


    holding_cost = 1
    setup_cost = 0
    unit_price = 0
    gamma = 1
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
    fn = outdir+'/'+prefix

    s = time.time()
    for t in range(21):
        for o in model.info_states():
            for x in range(30):
                print("state:", (t, x, o))
                model.j_function_la(t, x, o)
                print("\t", "order:", model.order_la(t, x, o))
                print("\t", "j_func:", model.j_function_la(t, x, o))
        model.to_pickle(fn)

    print("run time:", time.time() - s)
    print(model.value_function_j)
