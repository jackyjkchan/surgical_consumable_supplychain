import pandas as pd
from scm_optimization.model import StationaryOptModel
import plotly
import numpy as np
import textwrap
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from pprint import pprint

fn = 'scripts/optimization_model/results/mdp_policy_results_20190804_K=20.pickle'
data = pd.read_pickle(fn)
traces = []
t_max = max(data["t"])
df = data[data["inventory_position_state"] == 0]
df = df[df["inventory_position_state"] == 0]
df = df[df["t"] == t_max]

df["o_1"] = df["information_state"].apply(lambda x: x[0])
df["o_2"] = df["information_state"].apply(lambda x: x[1])
x_len = int(max(df["o_1"]) + 1)
y_len = int(max(df["o_2"]) + 1)

order_up_to_surface = df.groupby(["o_2"]).apply(lambda f: f.sort_values(by="o_1")["order_up_to"].to_list()).to_list()
base_stock_surface = df.groupby(["o_2"]).apply(lambda f: f.sort_values(by="o_1")["base_stock"].to_list()).to_list()

pprint(order_up_to_surface)
pprint(base_stock_surface)

title = '<br>'.join(
    textwrap.wrap("Optimal (S(o), s(o)) Ordering Policy as function of Information State with Horizon of 2",
                  width=80)
)
layout = go.Layout(title=title,
                   scene={
                       'xaxis': {'title': 'o_1'},
                       'yaxis': {'title': 'o_2'},
                       'zaxis': {'title': "Inventory Position"}}
                   )

fig = go.Figure(data=[
    go.Surface(z=order_up_to_surface, opacity=0.75, name="S(o1, o2) Order Up To"),
    go.Surface(z=base_stock_surface, showscale=False, opacity=0.75, name="s(o1, o2) Base Stock")],
    layout=layout
)
fig.update_traces(contours_z=dict(show=True, usecolormap=True,
                                  highlightcolor="green", project_z=True))

plot(fig, filename="Policy_Surface_K=20_20190804.html")

base_stock_df = df.groupby(["o_1"]).apply(lambda f: f.sort_values(by="o_2")["base_stock"].to_list())
order_up_to_df = df.groupby(["o_1"]).apply(lambda f: f.sort_values(by="o_2")["order_up_to"].to_list())
o_2_axis = df.groupby(["o_1"]).apply(lambda f: f.sort_values(by="o_2")["o_2"].to_list())

base_stock_traces = [go.Scatter(x=o_2_axis[o_1],
                                y=base_stock_df[o_1],
                                opacity=0.75,
                                name="Base Stock Level o_1={0:d}".format(int(o_1)))
                     for o_1 in base_stock_df.keys()]
order_up_to_traces = [go.Scatter(x=o_2_axis[o_1],
                                 y=order_up_to_df[o_1],
                                 opacity=0.75,
                                 name="Order Up To Level o_1={0:d}".format(int(o_1)))
                      for o_1 in base_stock_df.keys()]

layout = go.Layout(title="Structure of Optimal S(o), s(o) Policy for Information Horizon of 2",
                   xaxis={'title': 'o_2 State'},
                   yaxis={'title': 'Inventory Position'})

fig = go.Figure(data=base_stock_traces+order_up_to_traces,
                layout=layout
                )
plot(fig, filename="Policy_line_plots_K=20_20190804.html")
