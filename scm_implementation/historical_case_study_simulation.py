from scm_simulation.hospital import Hospital, HistoricalElectiveSurgeryDemandProcess, \
    HistoricalEmergencySurgeryDemandProcess
from scm_simulation.item import Item
from scm_simulation.surgery import Surgery
from scm_simulation.rng_classes import GeneratePoisson, GenerateFromSample, GenerateDeterministic
from scm_simulation.order_policy import AdvancedInfoSsPolicy
import pickle
import pandas as pd
import numpy as np
from datetime import date

"""
Relies on static objects in simulation_inputs as surgery schedule
Relies on static policy loaded from AdvancedInfoSsPolicy
One trajectory, one realization
"""


item_ids = ["47320", "56931", "1686", "129636", "83532", "38262", "83105", "83106"]
item_ids = ["83105", "83106"]
item_ids = ["21920", "38197", "82099"]
bs = [1000, 10000]


def run(item_id, b, n, lt):
    # item_id = "47320"
    # b = 100
    # n = 0

    fn = "scm_implementation/simulation_inputs/ns_policy_id_{}_b_{}_lt_{}_info_{}.pickle".format(item_id, b, lt, n)
    with open(fn, "rb") as f:
        policy = pickle.load(f)

    policy = {item_id: AdvancedInfoSsPolicy(item_id, policy)}

    order_lt = {item_id: GenerateDeterministic(lt)}

    # To filter out surgeries that exceed a right percentile, include options item_ids=["item_id"], threshold=0.01
    # i.e. HistoricalElectiveSurgeryDemandProcess(item_ids=["item_id"], threshold=0.01)
    elective_process = HistoricalElectiveSurgeryDemandProcess(item_ids=[item_id], threshold=0.01)
    emergency_process = HistoricalEmergencySurgeryDemandProcess(item_ids=[item_id], threshold=0.01)
    # elective_process = HistoricalElectiveSurgeryDemandProcess()
    # emergency_process = HistoricalEmergencySurgeryDemandProcess()

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

    return {"item_id": item_id,
            "backlogging_cost": b,
            "info_horizon": n,
            "lead_time": lt,
            "average_inventory_level": np.mean(hospital.full_inventory_lvl[item_id]),
            "surgeries_backlogged": stock_outs,
            "service_level": service_level
            }


if __name__ == "__main__":
    results = pd.DataFrame()
    for item_id in item_ids:
        #for lt in [0]:
        for lt in [0, 1]:
            for b in bs:
                for n in [0, 1, 2]:
                    r = run(item_id, b, n, lt=lt)
                    results = results.append(r, ignore_index=True)

    results.to_csv(str(date.today()) + "_historical_impl_summary.csv")




    # item_id="47320"
    # b = 1000
    # n=0
    # lt = 1
    #
    # fn = "scm_implementation/simulation_inputs/ns_policy_id_{}_b_{}_lt_{}_info_{}.pickle".format(item_id, b, lt, n)
    # with open(fn, "rb") as f:
    #     policy = pickle.load(f)
    # policy = {item_id: AdvancedInfoSsPolicy(item_id, policy)}
    # order_lt = {item_id: GenerateDeterministic(lt)}
    # elective_process = HistoricalElectiveSurgeryDemandProcess(item_ids=[item_id], threshold=0.01)
    # emergency_process = HistoricalEmergencySurgeryDemandProcess(item_ids=[item_id], threshold=0.01)
    # hospital = Hospital([item_id],
    #                     policy,
    #                     order_lt,
    #                     emergency_process,
    #                     elective_process,
    #                     warm_up=0,
    #                     sim_time=365,
    #                     end_buffer=lt)