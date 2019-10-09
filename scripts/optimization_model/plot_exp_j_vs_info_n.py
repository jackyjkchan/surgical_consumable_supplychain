import textwrap
import os
import pandas as pd
import pacal
import itertools
from datetime import date

import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot


from scripts.optimization_model.model_configs import action_increment_configs
from scripts.optimization_model.model_configs.leadtime_configs import poisson_usage

data = pd.read_pickle("scripts/optimization_model/results/2019-10-08_Non-Convex_Search_Usage_Model.pickle")
x = 0
t = max(data["t"])

C0 = pacal.ConstDistr(0)
groupbys = ['label', 'usage_model', 'gamma', 'holding_cost',
            'backlogging_cost', 'setup_cost', 'unit_price', 'information_horizon',
            'lead_time', 'increments']

data["information_horizon"] = data["info_state_rvs"].apply(lambda x:
                                                           len(x) - 1 if len(x) > 2 else 1 if x[1].mean() else 0
                                                           )

data = data[(data["inventory_position_state"] == x)]
data = data[(data["t"] == t)]
summary = data.groupby(groupbys).agg({"j_value_function": "mean"}).reset_index()

common_fields = []
common_values = []
diff_fields = []

for field in groupbys:
    if len(set(summary[field])) == 1:
        common_fields.append(field)
        common_values.append(summary[field][0])
    else:
        diff_fields.append(field)
diff_fields.remove("information_horizon")
diff_values = [set(summary[field]) for field in diff_fields]
combinations = list(itertools.product(*diff_values))

traces = []
for comb in combinations:
    d = summary
    for field, val in zip(diff_fields, comb):
        d = d[d[field] == val]
    label = "_".join(["{}={}".format(field, str(val)) for field, val in zip(diff_fields, comb)])
    traces.append(go.Scatter(
        x=d["information_horizon"],
        y=d['j_value_function'],
        name=label
    ))

title = " ".join(["{}={}".format(field, str(val)) for field, val in zip(common_fields, common_values)])
title = '<br>'.join(textwrap.wrap(title, width=80))

layout = go.Layout(title=title,
                   xaxis={'title': 'Information Horizon'},
                   yaxis={'title': 'Optimal Expected Cost'})
figure = go.Figure(
    data=traces,
    layout=layout
)
plot(figure,
     filename="Expected_Cost_For_Various_Levels_of_Advanced_Information_{}.html".format(date.today().isoformat()))
