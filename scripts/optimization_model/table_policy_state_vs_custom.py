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


"""
Extracts a policy table with the rows being the policy for various o_t states. The columns will be for some custom dim.
so if custom dim is planning horizon t, the table could look like

             t=1,      t=2,      t=3
o=(1, 1)    (S, s)    (S, s)    (S, s)
o=(1, 2)    (S, s)    (S, s)    (S, s)
o=(2, 1)    (S, s)    (S, s)    (S, s)
o=(2, 2)    (S, s)    (S, s)    (S, s)
"""

normalize = True
data = pd.read_pickle("scripts/optimization_model/results/2019-10-08_Non-Convex_Search_Usage_Model.pickle")
horizontal_dim = "t"
x = 0

groupbys = ['label', 'usage_model', 'gamma', 'holding_cost',
            'backlogging_cost', 'setup_cost', 'unit_price', 'information_horizon',
            'lead_time', 'increments']

# data["information_horizon"] = data["info_state_rvs"].apply(lambda x:
#                                                            len(x) - 1 if len(x) > 2 else 1 if x[1].mean() else 0
#                                                            )

data = data[(data["inventory_position_state"] == x)]
data["policy"] = data.apply(lambda row: (row["order_up_to"], row["base_stock"]), axis=1)

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

pt = pd.pivot_table(data, values="policy", index=diff_fields+["information_state"], columns="t", aggfunc=max)
pt.to_csv("Policy_Table.csv")