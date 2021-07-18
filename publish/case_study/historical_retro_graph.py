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
import matplotlib.pyplot as plt


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
    return hospital.full_inventory_lvl[item_id]


b = 10000
lt = 1
item_id = "21920"

d0 = run(item_id, b, 0, lt)
d1 = run(item_id, b, 1, lt)
d2 = run(item_id, b, 2, lt)

s = 7
e = s + 7*4*3
fig = plt.figure(figsize=(7, 4))
plt.plot(d0[s:e], color="#08519c", marker="x", label="0-ABI")
plt.plot(d1[s:e], color="#a50f15", marker="o", label="1-ABI")
plt.plot(d2[s:e], color="#006d2c", marker="+", label="2-ABI")
ax = plt.axes()
ax.set(xlabel='Day', ylabel='Inventory Level',
       title='')
plt.legend()
plt.savefig("historical_inventory_trace_{}".format(item_id) + ".svg", format='svg')
