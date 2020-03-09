from scm_simulation.hospital import Hospital, HistoricalElectiveSurgeryDemandProcess, \
    HistoricalEmergencySurgeryDemandProcess
from scm_simulation.item import Item
from scm_simulation.surgery import Surgery
from scm_simulation.rng_classes import GeneratePoisson, GenerateFromSample, GenerateDeterministic
from scm_simulation.order_policy import AdvancedInfoSsPolicy
import pickle
import pandas as pd
import numpy as np

"""
Relies on static objects in simulation_inputs as surgery schedule
Relies on static policy loaded from AdvancedInfoSsPolicy
One trajectory, one realization
"""

results = pd.DataFrame()
item_ids = ["47320", "56931", "1686", "129636", "83532", "38262"]
bs = [100, 1000, 10000]


def run(item_id, b, n):
    # item_id = "47320"
    # b = 100
    # n = 0

    fn = "scm_implementation/simulation_inputs/ns_policy_id_{}_b_{}_info_{}.pickle".format(item_id, b, n)
    with open(fn, "rb") as f:
        policy = pickle.load(f)

    policy = {item_id: AdvancedInfoSsPolicy(item_id, policy)}

    order_lt = {item_id: GenerateDeterministic(0)}
    surgery1 = Surgery(
        "surgery1",
        {"item_id": 1},
        {"item_id": GeneratePoisson(8)}
    )

    elective_process = HistoricalElectiveSurgeryDemandProcess()
    emergency_process = HistoricalEmergencySurgeryDemandProcess()

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

    average_inventory_level = np.mean(hospital.full_inventory_lvl[item_id])
    info_horizon = n
    stock_outs = sum(len(d) for d in hospital.full_surgery_backlog)
    return {"item_id": item_id,
            "backlogging_cost": b,
            "info_horizon": n,
            "average_inventory_level": np.mean(hospital.full_inventory_lvl[item_id]),
            "surgeries_backlogged": stock_outs
            }


if __name__ == "__main__":
    for item_id in item_ids:
        for b in bs:
            for n in [0, 1]:
                r = run(item_id, b, n)
                results = results.append(r, ignore_index=True)
