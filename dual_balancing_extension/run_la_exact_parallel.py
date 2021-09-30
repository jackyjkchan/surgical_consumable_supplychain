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

time.time()


def run_la_parallel(arg):
    fn = arg["fn"]
    t = arg["t"]
    o_vec = arg["o_vec"]
    segment_num = arg["segment_num"]
    #model = arg["model"]

    time.sleep(1)
    time.sleep(segment_num/2)
    model = LA_DB_Model.read_pickle(fn + "_model.pickle")
    for o in o_vec:
        for x in range(21):
            model.j_function_la(t, x, o)
            print("state:", (t, x, o))
            print("\t", "order:", model.order_la(t, x, o))
            print("\t", "j_func:", model.j_function_la(t, x, o))

    return model


if __name__ == "__main__":
    num_pools = os.cpu_count()-1
    print("pools:", num_pools)
    pool = Pool(num_pools)
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

    print(fn)
    if os.path.isfile(fn+"_model.pickle"):
        model = LA_DB_Model.read_pickle(fn+"_model.pickle")
        print("model found")
    else:
        model.to_pickle(fn)
        print("model not found")

    s = time.time()
    for t in range(21):
        o_vec = list(o for o in model.info_states())
        o_vecs = [o_vec[i::num_pools] for i in range(num_pools)]

        random.shuffle(o_vec)

        args = []
        for i in range(num_pools):
            arg = {
                "fn": fn,
                "t": t,
                "o_vec": o_vecs[i],
                "segment_num": i
            }
            args.append(arg)
        sub_models = pool.map(run_la_parallel, args)

        for sub_model in sub_models:
            model.value_function_j.update(sub_model.value_function_j)
            model.value_function_v.update(sub_model.value_function_v)
            model.order_la_cache.update(sub_model.order_la_cache)

        print(time.time() - s)
        prefix2 = prefix+"_t_{}".format(t)
        model.to_pickle(outdir+'/'+prefix2)
        model.to_pickle(fn)
        time.sleep(2)

    print("run time:", time.time() - s)
    print(model.value_function_j)
