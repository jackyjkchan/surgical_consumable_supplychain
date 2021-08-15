from scm_optimization.integer_dual_balancing import DualBalancing
from random import random
from scm_optimization.model import *
from scipy.optimize import minimize, bisect, minimize_scalar
from dual_balancing_extension.simulation import Hospital_LA_MDP, Hospital_DB_MDP
import pandas as pd
import pickle
import sys


time.time()


def run_sim(args):
    backlogging_cost = args['backlogging_cost']
    info = args['info']
    rep = args['rep']
    outdir = args['outdir']


    start_time = time.time()
    results = pd.DataFrame()

    lead_time = 0
    holding_cost = 1
    setup_cost = 0
    unit_price = 0
    gamma = 1

    usage_model = PoissonUsageModel(scale=1, trunk=1e-3)
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

    hospital = Hospital_DB_MDP(db_model=model, periods=21)
    hospital.run()

    result = {
        "info": info,
        "backlogging_cost": backlogging_cost,
        "rep": rep,
        "cost_la": hospital.cost_incurred_db,
        "backlog_cost_incurred_db": hospital.backlog_cost_incurred_db,
        "holding_cost_incurred_db": hospital.holding_cost_incurred_db,

        "cost_mdp": hospital.cost_incurred_mdp,
        "backlog_cost_incurred_mdp": hospital.backlog_cost_incurred_mdp,
        "holding_cost_incurred_mdp": hospital.holding_cost_incurred_mdp,

        "schedule": hospital.schedule,
        "demand": hospital.demand,
        "order_db": hospital.order_db,
        "inventory_db": hospital.inventory_level_db,
        "order_mdp": hospital.order_mdp,
        "order_upto": hospital.order_up_to_mdp,
        "inventory_mdp": hospital.inventory_level_mdp,

        "run_time_min": (time.time() - start_time) / 60
    }

    results = results.append(result, ignore_index=True)
    print(results)
    results_fn = outdir + "/db_results_b_{}_{}_r_{}_{}.csv".format(str(backlogging_cost),
                                                                   str(info),
                                                                   str(rep),
                                                                   datetime.now().strftime("%Y-%M-%d_%H%M%S%f")
                                                                   )
    results.to_csv(results_fn, index=False)
    return results_fn


if __name__ == "__main__":

    outdir = sys.argv[1] if len(sys.argv) > 1 else "db_results"

    backlogging_costs = [10, 100, 1000]
    infos = [0, 1, 2, 3]
    reps = list(range(100))

    args_list = []
    for backlogging_cost in backlogging_costs:
        for info in infos:
            for rep in reps:
                args_list.append(
                    {"backlogging_cost": backlogging_cost,
                     "info": info,
                     "rep": rep,
                     "outdir":outdir}
                )

    results_files = []
    for arg in args_list:
        run_sim(arg)
        results_files.append(run_sim(arg))

    all_results = pd.DataFrame()
    for fn in results_files:
        all_results = pd.concat([all_results, pd.read_csv(fn)])
    all_results.to_csv(outdir + "/ALL_RESULTS_{}.csv".format(datetime.now().strftime("%Y-%M-%d_%H%M%S%f")), index=False)
