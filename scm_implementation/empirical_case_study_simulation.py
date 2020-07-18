from scm_simulation.hospital import Hospital, EmpiricalElectiveSurgeryDemandProcess, \
    EmpiricalEmergencySurgeryDemandProcess, ParametricEmergencySurgeryDemandProcessWithPoissonUsage, \
    ParametricElectiveSurgeryDemandProcessWithPoissonUsage, \
    ParametricEmergencySurgeryDemandProcessWithTruncatedPoissonUsage, \
    ParametricElectiveSurgeryDemandProcessWithTruncatedPoissonUsage

from scm_simulation.item import Item
from scm_simulation.surgery import Surgery
from scm_simulation.rng_classes import GeneratePoisson, GenerateFromSample, GenerateDeterministic
from scm_simulation.order_policy import AdvancedInfoSsPolicy
import pickle
import pandas as pd
import numpy as np
from multiprocessing import Pool
from datetime import datetime, date

"""
Elective and emergency surgeries per day are empirically generated
Surgery definition are empirically generated (random sampling from all historical surgeries)
Surgery item usage are based on historical
"""


def run(args):
    seed = 0
    item_id, b, n, lt, seed = args
    # item_id = "47320"
    # b = 100
    # n = 0

    fn = "scm_implementation/simulation_inputs/ns_policy_id_{}_b_{}_lt_{}_info_{}.pickle".format(item_id, b, lt, n)
    with open(fn, "rb") as f:
        policy = pickle.load(f)

    policy = {item_id: AdvancedInfoSsPolicy(item_id, policy)}
    order_lt = {item_id: GenerateDeterministic(lt)}
    # elective_process = EmpiricalElectiveSurgeryDemandProcess(seed=seed)
    # emergency_process = EmpiricalEmergencySurgeryDemandProcess(seed=seed)
    # elective_process = ParametricElectiveSurgeryDemandProcessWithPoissonUsage(seed=seed)
    # emergency_process = ParametricEmergencySurgeryDemandProcessWithPoissonUsage(seed=seed)
    elective_process = ParametricElectiveSurgeryDemandProcessWithTruncatedPoissonUsage(seed=seed)
    emergency_process = ParametricEmergencySurgeryDemandProcessWithTruncatedPoissonUsage(seed=seed)

    hospital = Hospital([item_id],
                        policy,
                        order_lt,
                        emergency_process,
                        elective_process,
                        warm_up=7,
                        sim_time=365,
                        end_buffer=7)

    hospital.run_simulation()
    hospital.trim_data()

    stock_outs = sum(len(d) for d in hospital.full_surgery_backlog)
    service_level = sum(len(d) for d in hospital.full_elective_schedule) \
                    + sum(len(d) for d in hospital.full_emergency_schedule)
    service_level = 1 - stock_outs / service_level
    r = {"item_id": item_id,
         "backlogging_cost": b,
         "info_horizon": n,
         "lead_time": lt,
         "average_inventory_level": np.mean(hospital.full_inventory_lvl[item_id]),
         "full_inventory_lvl": hospital.full_inventory_lvl[item_id],
         "surgeries_backlogged": stock_outs,
         "service_level": service_level,
         "seed": seed
         }
    print("Finished: ", datetime.now().isoformat(), "-", item_id, b, n, seed)
    return r


if __name__ == "__main__":

    def halfwidth(series):
        return 1.96 * np.std(series) / np.sqrt(len(series))


    pool = Pool(10)
    results = pd.DataFrame()
    item_ids = ["47320", "56931", "1686", "129636", "83532", "38262"]
    item_ids = ["83105", "83106"]
    item_ids = ["1686"]
    bs = [1000, 10000]
    lts = [0, 1]
    ns = [0, 1, 2]

    # item_ids = ["129636"]
    # bs = [1000]
    # lts = [1]
    # ns = [0, 1, 2]

    all_args = []

    for item_id in item_ids:
        for lt in lts:
            for b in bs:
                for n in ns:
                    for seed in range(0, 500):
                        all_args.append((item_id, b, n, lt, seed))
    # all_args = all_args[0:10]
    rs = pool.map(run, all_args)
    for r in rs:
        results = results.append(r, ignore_index=True)

    results.to_pickle(str(date.today()) + "_parametric_case_study_1686.pickle")

    # summary = results.groupby(["backlogging_cost", "info_horizon", "lead_time", "item_id"]) \
    #     .agg({"surgeries_backlogged": ["mean", "std", halfwidth],
    #           "average_inventory_level": ["mean", "std", halfwidth],
    #           "service_level": ["mean", "std", halfwidth]})
    # summary = summary.pivot_table(["average_inventory_level", "surgeries_backlogged", "service_level"],
    #                               ["backlogging_cost", "lead_time", "item_id"], ["info_horizon"])
    # summary.to_csv(str(date.today()) + "_parametric_case_study_summary_truncated_100-500.csv")
