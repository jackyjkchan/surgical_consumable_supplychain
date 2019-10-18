import textwrap
import os
import pandas as pd
import pacal
import itertools
from datetime import date
import numpy as np
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.express as px

from scm_optimization.model import *

models = [
    "scripts/optimization_model/results/2019-10-10_Non_Convex_Search_Det_Usage_Simple_{}.pickle_model.pickle".format(
        str(i))
    for i in range(1, 9)
]

results_df = pd.DataFrame()

for fn in models:
    model = StationaryOptModel.read_pickle(fn)
    t_max = max(state[0] for state in model.value_function_j)
    info_states = model.info_states()
    info_horizon = 0 if len(info_states) == 1 else len(info_states[0])
    x_max = max(model.stock_up_level(t_max, o) for o in info_states)
    x_min = int(-max(rv.get_piecewise_pdf().getDiracs()[-1].a for rv in model.info_state_rvs))
    all_states = [(x, o) for x in range(x_min, x_max + 1) for o in info_states]
    policy = {o: (model.stock_up_level(t_max, o),
                  model.base_stock_level(t_max, o)) for o in info_states}

    transition_df = pd.DataFrame(columns={"source": [],
                                          "sink": [],
                                          "p": []})
    for source in all_states:
        x = source[0]
        o = source[1]

        stock_up_lvl = policy[o][0]
        base_stock_lvl = policy[o][1]
        y = stock_up_lvl if x <= base_stock_lvl else x

        transitions = model.unpack_state_transition(*model.state_transition(t_max, y, o))
        sink_states = [(state[1], state[2]) for state in transitions[0]]
        sink_probabilities = [p for p in transitions[1]]
        for sink, p in zip(sink_states, sink_probabilities):
            transition_df = transition_df.append({"source": source,
                                                  "sink": sink,
                                                  "p": p},
                                                 ignore_index=True)

    while len(set(transition_df["source"])) != len(set(transition_df["sink"])):
        transition_df = transition_df[transition_df["source"].isin(set(transition_df["sink"]))]
    matrix = transition_df.pivot(index="source", columns="sink", values="p").fillna(0)

    summary_df = pd.DataFrame()
    summary_df["state"] = matrix.reset_index()["source"]

    t_matrix = np.matrix(matrix)
    state = np.array([1/len(matrix)]*len(matrix))
    next = state.dot(t_matrix)
    trials = 0

    while np.linalg.norm(state-next):
        trials += 1
        state = next
        next = state.dot(t_matrix)
        if trials > 1000:
            break

    summary_df["p"] = state.tolist()[0]
    summary_df["y"] = summary_df["state"].apply(lambda s: policy[s[1]][0] if s[0] <= policy[s[1]][1] else s[0])
    summary_df["order_cost"] = summary_df["state"].apply(lambda s: model.k if s[0] <= policy[s[1]][1] else 0)
    summary_df["G"] = summary_df.apply(lambda row:
                                       model.G_future(row["y"], row["state"][1]), axis=1)
    summary_df["Cost"] = summary_df.apply(lambda row:
                                       row["order_cost"] + row["G"], axis=1)

    cost = np.matrix(summary_df["Cost"]).transpose()
    j = cost
    next = cost + model.gamma*t_matrix.dot(j)
    trials = 0
    while np.linalg.norm(j-next):
        trials += 1
        j = next
        next = cost + model.gamma * t_matrix.dot(j)
        if trials > 1000:
            break
    summary_df["j_value_finite_horizon"] = summary_df["state"].apply(lambda s: model.j_function(t_max, *s))
    summary_df["j_value"] = j
    summary_df["state_str"] = summary_df["state"].apply(lambda x: str(x))

    fn = "info_horizon_{}.html".format(str(info_horizon))
    fig = px.bar(summary_df, x='state_str', y='p',
                 hover_data=['y', 'order_cost', 'G', 'Cost'], color='Cost', height=400)
    plot(fig, filename=fn)

    results_df = results_df.append({
        "horizon": info_horizon,
        "j_value": sum(summary_df["p"]*summary_df["j_value"]),
        "order_prob": sum(summary_df[summary_df["order_cost"] > 0]["p"]),
        "expected_x": sum(summary_df.apply(lambda row: row["p"] * row["state"][0], axis=1)),
        "expected_x|x>0": sum(summary_df.apply(lambda row: row["p"]*row["state"][0] if row["state"][0] > 0 else 0,
                                               axis=1)),
        "stockout_prob": sum(summary_df[summary_df["state"].apply(lambda x: x[0] < 0)]["p"])
    }, ignore_index=True)

    print(summary_df)
print(results_df)
results_df.to_csv("steady_state_results.csv")