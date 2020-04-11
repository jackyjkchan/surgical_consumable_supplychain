import textwrap
import os
import pickle
import pandas as pd
import pacal
import itertools
from datetime import date

import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot


from scripts.optimization_model.model_configs import action_increment_configs

"scm_implementation/results/2020-01-22_ns_impl_38262.pickle"
"scm_implementation/results/2020-01-22_ns_impl_83532.pickle"
"scm_implementation/results/2020-01-22_ns_impl_129636.pickle"
item_ids = ["47320", "56931", "1686", "129636", "83532", "38262"]
l = 0


for item_id in item_ids:
    data = pd.read_pickle(
        "scm_implementation/results/2020-01-22_ns_impl_{}.pickle".format(item_id))
    #data = pd.read_pickle(
    #    "scm_implementation/results/2020-04-08_ns_impl_LT_1_{}.pickle".format(item_id))
    leadtimes = set(data["lead_time"])
    ts = [max(data["t"]) - i for i in range(7)]
    bs = set(data["backlogging_cost"])
    for n in [0, 1, 2]:
        for l in leadtimes:
            for b in bs:
                # list of dictionaries, ns_policy[0] is monday policy etc
                # policy is form of info_state: order_up_to_level
                ns_policy = [{} for _ in range(7)]
                for t in ts:
                    rt = (-t - 1) % 7
                    df = data[data["t"] == t]
                    df = df[df["information_horizon"]==n]
                    df = df[df["backlogging_cost"]==b]

                    states = df["information_state"]
                    order_up_level = df["order_up_to"]
                    ns_policy[rt] = {state: (level, level-1) for state, level in zip(states, order_up_level)}

                fn = "scm_implementation/simulation_inputs/ns_policy_id_{}_b_{}_lt_{}_info_{}.pickle".format(item_id,
                                                                                                       str(int(b)),
                                                                                                       str(l),
                                                                                                       str(n))
                with open(fn, "wb") as f:
                    pickle.dump(ns_policy, f)
                    print(fn)
                    print(ns_policy)



