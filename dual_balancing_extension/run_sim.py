from scm_optimization.integer_dual_balancing import DualBalancing
from random import random
from scm_optimization.model import *
from scipy.optimize import minimize, bisect, minimize_scalar
from dual_balancing_extension.simulation import Hospital
import pandas as pd
import pickle
import sys
time.time()

if __name__ == "__main__":
    start_time = time.time()
    print(sys.argv)
    rep = sys.argv[1] if len(sys.argv) > 1 else 0

    backlogging_cost = 1000
    info = 1

    lead_time = 0

    results = pd.DataFrame()

    holding_cost = 1
    setup_cost = 0
    unit_price = 0
    gamma = 1

    usage_model = PoissonUsageModel(scale=1)


    results_fn = "db_results/db_results_b_{}_{}_r_{}.csv".format(str(backlogging_cost),
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

    hospital = Hospital(db_model=model, periods=20)
    hospital.run()

    results = results.append({
        "info": info,
        "backlogging_cost": backlogging_cost,
        "rep": rep,
        "cost": hospital.cost_incurred,
        "backlog_cost_incurred": hospital.backlog_cost_incurred,
        "holding_cost_incurred": hospital.holding_cost_incurred,
        "schedule": hospital.schedule,
        "order_cont": hospital.order_continuous,
        "order": hospital.order,
        "demand": hospital.demand,
        "inventory": hospital.inventory_level,
        "run_time_min": (time.time() - start_time)/60
    }, ignore_index=True)
    results.to_csv(results_fn)

