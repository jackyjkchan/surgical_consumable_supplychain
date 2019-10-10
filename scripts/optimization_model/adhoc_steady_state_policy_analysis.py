import textwrap
import os
import pandas as pd
import pacal
import itertools
from datetime import date

import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

from scm_optimization.model import DeterministUsageModel

data = pd.read_pickle("scripts/optimization_model/results/2019-10-08_Non-Convex_Search_Usage_Model.pickle")
horizontal_dim = "t"
x = 0

groupbys = ['label', 'usage_model', 'gamma', 'holding_cost',
            'backlogging_cost', 'setup_cost', 'unit_price', 'information_horizon',
            'lead_time', 'increments']
model_params = ['label', 'usage_model', 'gamma', 'holding_cost',
            'backlogging_cost', 'setup_cost', 'unit_price', 'information_horizon',
            'lead_time', '']


model = {
    'usage_model': DeterministUsageModel(1),
    'gamma': 0.9,
    'holding_cost': 1,
    'backlogging_cost': 10,
    'setup_cost': 50
}
data = data[data["inventory_position_state"]==0]
for field in model:
    data = data[data[field] == model[field]]
t_max = max(data['t'])

for n in sorted(set(data["information_horizon"])):
    print(n)
    policy_df = data[(data["information_horizon"]==n) & (data["t"]==t_max)][[72q8/1""]]


# data["information_horizon"] = data["info_state_rvs"].apply(lambda x:
#                                                            len(x) - 1 if len(x) > 2 else 1 if x[1].mean() else 0
#                                                            )

data = data[(data["inventory_position_state"] == x)]
data["policy"] = data.apply(lambda row: (row["order_up_to"], row["base_stock"]), axis=1)
data[]

common_fields = []
common_values = []
diff_fields = []

for field in groupbys:
    if len(set(data[field])) == 1:
        common_fields.append(field)
        common_values.append(data[field].iloc[0])
    else:
        diff_fields.append(field)
diff_fields.remove("information_horizon")
diff_values = [sorted(set(data[field])) for field in diff_fields]
