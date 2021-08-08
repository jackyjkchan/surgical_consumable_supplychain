from scm_optimization.integer_dual_balancing import DualBalancing
from random import random
from scm_optimization.model import *
from scipy.optimize import minimize, bisect, minimize_scalar
from dual_balancing_extension.simulation import Hospital_LA_MDP
import pandas as pd
import pickle
import sys
time.time()

if __name__ == "__main__":
    start_time = time.time()


    backlogging_cost = 1000
    info = 1
    lead_time = 0

    results = pd.DataFrame()

    holding_cost = 1
    setup_cost = 0
    unit_price = 0
    gamma = 1

    for rep in range(2500):
        usage_model = PoissonUsageModel(scale=1, trunk=1e-3)
        results_fn = "la_results/la_results_b_{}_{}_r_{}.csv".format(str(backlogging_cost),
                                                                     str(info),
                                                                     str(rep)
                                                                     )


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

        print("backlogging cost:", backlogging_cost, " info: ", info, " rep: ", rep)

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

            "run_time_min": (time.time() - start_time)/60
        }

        results = results.append(result, ignore_index = True)
        print(results)
        results.to_csv(results_fn)

