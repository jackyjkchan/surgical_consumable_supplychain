import pandas as pd
from scm_optimization.model import StationaryOptModel
import plotly
import textwrap
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import pacal


def test_case_var(info_states):
    weight = 1 / len(info_states)
    pdf = sum([weight * pacal.PoissonDistr(info_state).get_piecewise_pdf() for info_state in info_states])
    d_rv = pacal.DiscreteDistr([d.a for d in pdf.getDiracs()], [d.f for d in pdf.getDiracs()])
    return d_rv.var()


def demand_var(info_rv):
    pdf = sum([dirac.f * pacal.PoissonDistr(dirac.a).get_piecewise_pdf() for dirac in
               info_rv.get_piecewise_pdf().getDiracs()])
    d_rv = pacal.DiscreteDistr([d.a for d in pdf.getDiracs()], [d.f for d in pdf.getDiracs()])
    return d_rv.var()


fn = 'scripts/optimization_model/results/batch_mdp_results_usage_model_20190915_merged.pickle'
data = pd.read_pickle(fn)
traces = []

usage_models_p = {
    "Poisson": 0,
    "Binomial p=8/32": 8 / 32,
    "Binomial p=8/16": 8 / 16,
    "Binomial p=8/13": 8 / 13,
    "Binomial p=8/11": 8 / 11,
    "Binomial p=8/9": 8 / 9,
    "Deterministic": 1
}

test_cases_usage_var = pd.DataFrame({"label": list(usage_models_p.keys()),
                                     "usage_variance": list(usage_models_p.values())})
test_cases_usage_var["usage_variance"] = test_cases_usage_var["usage_variance"].apply(lambda p: 8 * (1 - p))
data = data.join(test_cases_usage_var.set_index("label"),
                 on="usage_model",
                 how="left",
                 rsuffix="label")

# traces = []
# for label in set(data["exogenous_label"]):
#     for k in set(data["setup_cost"]):
#         print(label)
#         df = data[(data["inventory_position_state"] == 0) * (data["t"] == t_max)]
#         df = df[df["exogenous_label"] == label]
#         df = df[df['setup_cost'] == k]
#         summary = df \
#             .groupby(["information_horizon"]) \
#             .agg({"j_value_function": "mean"}) \
#             .reset_index()
#
#         traces.append(go.Scatter(
#             x=list(range(len(summary['information_horizon']))),
#             y=summary['j_value_function'],
#             name=label + " K = {0}".format(str(k))
#         )
#         )
# title = '<br>'.join(
#     textwrap.wrap("Expected Optimal Cost for Various Levels of Advanced Information at 0 Initial Inventory ",
#                   width=80)
# )
# layout = go.Layout(title=title,
#                    xaxis={'title': 'Information Horizon'},
#                    yaxis={'title': 'Optimal Expected Cost'})
# figure = go.Figure(
#     data=traces,
#     layout=layout
# )
# plot(figure, filename="Expected_Cost_For_Various_Levels_of_Advanced_Information_Multi_K.html")

# Plot the Expected Optimal Cost, E[J(0, .)] against Usage variance while holding daily demand constant.
t_max = max(data['t'])
summary = data[(data["inventory_position_state"] == 0) * (data["t"] == t_max)] \
    .groupby(["usage_variance", "information_horizon", "setup_cost"]) \
    .agg({"j_value_function": "mean"}) \
    .reset_index()
traces = []

line_styles = ("solid", "dot", "dash", "dashdot", "longdash", "longdashdot")
style_index = 0
for information_horizon in set(summary["information_horizon"]):
    for setup_cost in set(summary["setup_cost"]):
        df = summary[summary["information_horizon"] == information_horizon]
        df = df[df["setup_cost"] == setup_cost]

        traces.append(
            go.Scatter(
                x=df['usage_variance'],
                y=df['j_value_function'],
                #name="info_horizon = {0}, K={1}".format(information_horizon, str(setup_cost)),
                name="info_horizon = {0}".format(information_horizon),
                line=dict(dash=line_styles[style_index % len(line_styles)])
            )
        )
        style_index += 1

title = '<br>'.join(
    textwrap.wrap("Expected Optimal Cost, E[J(0, .)], Against Usage Variance at Constant Daily Expected Demand",
                  width=80)
)
layout = go.Layout(title=title,
                   xaxis={'title': 'Usage Variance'},
                   yaxis={'title': 'Optimal Expected Cost'})

figure = go.Figure(
    data=traces,
    layout=layout
)

plot(figure, filename="Expected_Cost_Against_Usage_Variance_for_Various_Info_Horizon.html")

# pivot tables for order up to and base stock levels against n=3 information state for various usage variance
info_state_scale = {
    "Poisson": 1,
    "Binomial p=8/32": 8 / 32,
    "Binomial p=8/16": 8 / 16,
    "Binomial p=8/13": 8 / 13,
    "Binomial p=8/11": 8 / 11,
    "Binomial p=8/9": 8 / 9,
    "Deterministic": 1
}
for n in range(4):
    summary = data[(data["inventory_position_state"] == 0) *
                   (data["t"] == t_max) *
                   (data["information_horizon"] == n)]
    summary["expected_demand_state"] = summary.apply(
        lambda row: tuple(int(o * info_state_scale[row["usage_model"]]) for o in row["information_state"]), axis=1
    )
    order_up_to_df = summary.pivot(index='expected_demand_state', columns='usage_variance', values='order_up_to')
    base_stock_df = summary.pivot(index='expected_demand_state', columns='usage_variance', values='base_stock')

    order_up_to_df.to_csv("order_up_to_n={0}.csv".format(str(n)))
    base_stock_df.to_csv("base_stock_n={0}.csv".format(str(n)))
