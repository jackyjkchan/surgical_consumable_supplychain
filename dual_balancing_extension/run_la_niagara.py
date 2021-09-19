from scm_optimization.integer_dual_balancing import DualBalancing
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

    outdir = sys.argv[1] if len(sys.argv) > 1 else "la_results"
    backlogging_cost = int(sys.argv[2]) if len(sys.argv) > 1 else 1000
    info = int(sys.argv[3]) if len(sys.argv) > 1 else 0
    binom_usage_n = int(sys.argv[4]) if len(sys.argv) == 5 else 0

    lead_time = 0

    results = pd.DataFrame()

    holding_cost = 1
    setup_cost = 0
    unit_price = 0
    gamma = 1
    usage_model = BinomUsageModel(n=binom_usage_n, p=1 / binom_usage_n) if binom_usage_n else PoissonUsageModel(scale=1,
                                                                                                                trunk=1e-3)

    info_state_rvs = [pacal.ConstDistr(0)] * info + \
                     [pacal.BinomialDistr(10, 0.5)]

    model = DualBalancing(gamma,
                          lead_time,
                          info_state_rvs,
                          holding_cost,
                          backlogging_cost,
                          setup_cost,
                          unit_price,
                          usage_model=usage_model)

    print("backlogging cost:", backlogging_cost, " info: ", info)

    for rep in range(100):

        hospital = Hospital_LA_MDP(la_model=model, periods=21)
        hospital.run()

        result = {
            "info": info,
            "backlogging_cost": backlogging_cost,
            "rep": rep,
            "cost_la": hospital.cost_incurred_la,
            "backlog_cost_incurred_la": hospital.backlog_cost_incurred_la,
            "holding_cost_incurred_la": hospital.holding_cost_incurred_la,

            "cost_mdp": hospital.cost_incurred_mdp,
            "backlog_cost_incurred_mdp": hospital.backlog_cost_incurred_mdp,
            "holding_cost_incurred_mdp": hospital.holding_cost_incurred_mdp,

            "schedule": hospital.schedule,
            "demand": hospital.demand,
            "order_la": hospital.order_la,
            "inventory_la": hospital.inventory_level_la,
            "order_mdp": hospital.order_mdp,
            "order_upto": hospital.order_up_to_mdp,
            "inventory_mdp": hospital.inventory_level_mdp,

            "run_time_min": (time.time() - start_time) / 60
        }
        if binom_usage_n:
            result["binomial_n"] = binom_usage_n
            result["binomial_p"] = 1 / binom_usage_n,

        results_fn = "la_binomial_usage_results/la_results_b_{}_n_{}_{}_r_{}_{}.csv".format(str(backlogging_cost),
                                                                                            str(binom_usage_n),
                                                                                            str(info),
                                                                                            str(rep),
                                                                                            datetime.now().strftime(
                                                                                                "%Y-%m-%d_%H%M_%S_%f")
                                                                                            ) if binom_usage_n \
            else \
            "la_results/la_results_b_{}_{}_r_{}_{}.csv".format(str(backlogging_cost),
                                                               str(info),
                                                               str(rep),
                                                               datetime.now().strftime("%Y-%m-%d_%H%M_%S_%f")
                                                               )
        
        results = results.append(result, ignore_index=True)
        print(results)
        results.to_csv(outdir + "/" + results_fn)
