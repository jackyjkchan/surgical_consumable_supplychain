from scm_simulation.hospital import Hospital, EmpiricalElectiveSurgeryDemandProcess, \
    EmpiricalEmergencySurgeryDemandProcess, EmpiricalEmergencySurgeryDemandProcessWithPoissonUsage, \
    EmpiricalElectiveSurgeryDemandProcessWithPoissonUsage
from scm_simulation.item import Item
from scm_simulation.surgery import Surgery
from scm_simulation.rng_classes import GeneratePoisson, GenerateFromSample, GenerateDeterministic
from scm_simulation.order_policy import AdvancedInfoSsPolicy
import pickle
import pandas as pd
import numpy as np
from multiprocessing import Pool
from datetime import datetime

"""
Elective and emergency surgeries per day are empirically generated
Surgery definition are empirically generated (random sampling from all historical surgeries)
Surgery item usage are based on historical
"""


def run(args):
    seed = 0
    item_id, b, n, seed = args
    # item_id = "47320"
    # b = 100
    # n = 0

    fn = "scm_implementation/simulation_inputs/ns_policy_id_{}_b_{}_info_{}.pickle".format(item_id, b, n)
    with open(fn, "rb") as f:
        policy = pickle.load(f)

    policy = {item_id: AdvancedInfoSsPolicy(item_id, policy)}
    order_lt = {item_id: GenerateDeterministic(0)}
    #elective_process = EmpiricalElectiveSurgeryDemandProcess(seed=seed)
    elective_process = EmpiricalElectiveSurgeryDemandProcessWithPoissonUsage(seed=seed)
    #emergency_process = EmpiricalEmergencySurgeryDemandProcess(seed=seed)
    emergency_process = EmpiricalEmergencySurgeryDemandProcessWithPoissonUsage(seed=seed)

    hospital = Hospital([item_id],
                        policy,
                        order_lt,
                        emergency_process,
                        elective_process,
                        warm_up=0,
                        sim_time=365,
                        end_buffer=0)

    hospital.run_simulation()
    hospital.trim_data()

    stock_outs = sum(len(d) for d in hospital.full_surgery_backlog)

    r = {"item_id": item_id,
            "backlogging_cost": b,
            "info_horizon": n,
            "average_inventory_level": np.mean(hospital.full_inventory_lvl[item_id]),
            "surgeries_backlogged": stock_outs,
            "seed": seed
            }
    print("Finished: ", datetime.now().isoformat(), "-", item_id, b, n, seed)
    return r


if __name__ == "__main__":

    def halfwidth(series):
        return 1.96 * np.std(series) / np.sqrt(len(series))


    pool = Pool(8)
    results = pd.DataFrame()
    item_ids = ["47320", "56931", "1686", "129636", "83532", "38262"]
    bs = [100, 1000, 10000]

    all_args = []

    for item_id in item_ids:
        for b in bs:
            for n in [0, 1]:
                for seed in range(100):
                    all_args.append((item_id, b, n, seed))

    rs = pool.map(run, all_args)
    for r in rs:
        results = results.append(r, ignore_index=True)

    results.to_csv("empirical_case_study_results.csv")

    summary = results.groupby(["backlogging_cost", "info_horizon", "item_id"]) \
        .agg({"surgeries_backlogged": ["mean", "std", halfwidth],
              "average_inventory_level": ["mean", "std", halfwidth]})
    summary = summary.pivot_table(["average_inventory_level", "surgeries_backlogged"],
                                  ["backlogging_cost", "item_id"], ["info_horizon"])
    summary.to_csv("empirical_case_study_summary.csv")
