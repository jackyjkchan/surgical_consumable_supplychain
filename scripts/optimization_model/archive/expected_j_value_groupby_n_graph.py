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


fn = 'scripts/optimization_model/results/batch_mdp_results_non_convex_cases_trunk_10E-5_20191002_merged.pickle'
data = pd.read_pickle(fn)
traces = []

test_cases_var = {
    "E[Demand] 5": test_case_var([5]),
    "E[Demand] 3, 7": test_case_var([3, 7]),
    "E[Demand] 1, 9": test_case_var([1, 9]),
    "E[Demand] 0, 10": test_case_var([0, 10]),
    "E[Demand] 7, 13": test_case_var([7, 13]),
    "E[Demand] 6, 14": test_case_var([4, 16]),
    "E[Demand] 5, 15": test_case_var([5, 15])
    # "Poisson": pacal.PoissonDistr(8, trunk_eps=1e-3),
    # "Binomial p=8/32": pacal.BinomialDistr(32, p=0.25),
    # "Binomial p=8/16": pacal.BinomialDistr(16, p=0.5),
    # "Binomial p=8/13": pacal.BinomialDistr(13, p=8/13),
    # "Binomial p=8/11": pacal.BinomialDistr(11, p=8/11),
    # "Binomial p=8/10": pacal.BinomialDistr(10, p=8/10),
    # "Binomial p=8/9": pacal.BinomialDistr(9, p=8/9),
    # "Deterministic": pacal.ConstDistr(8)
}

test_cases_var = pd.DataFrame({"label": list(test_cases_var.keys()), "var": list(test_cases_var.values())})
data = data.join(test_cases_var.set_index("label"),
                 on="exogenous_label",
                 how="left",
                 rsuffix="label")

t_max = max(data['t'])
traces = []
for label in set(data["exogenous_label"]):
    for k in set(data["setup_cost"]):
        print(label)
        df = data[(data["inventory_position_state"] == 0) * (data["t"] == t_max)]
        df = df[df["exogenous_label"] == label]
        df = df[df['setup_cost'] == k]
        summary = df \
            .groupby(["information_horizon"]) \
            .agg({"j_value_function": "mean"}) \
            .reset_index()

        traces.append(go.Scatter(
            x=list(range(len(summary['information_horizon']))),
            y=summary['j_value_function'],
            name=label + " K = {0}".format(str(k))
        )
        )
title = '<br>'.join(
    textwrap.wrap("Expected Optimal Cost for Various Levels of Advanced Information at 0 Initial Inventory ",
                  width=80)
)
layout = go.Layout(title=title,
                   xaxis={'title': 'Information Horizon'},
                   yaxis={'title': 'Optimal Expected Cost'})
figure = go.Figure(
    data=traces,
    layout=layout
)
plot(figure, filename="Expected_Cost_For_Various_Levels_of_Advanced_Information_Multi_K_Non_Convex_Search_1e-5_trunk.html")

summary = data[(data["inventory_position_state"] == 0) * (data["t"] == t_max)] \
    .groupby(["var", "information_horizon", "setup_cost"]) \
    .agg({"j_value_function": "mean"}) \
    .reset_index()
traces = []
for information_horizon in set(summary["information_horizon"]):
    for setup_cost in set(summary["setup_cost"]):
        df = summary[summary["information_horizon"] == information_horizon]
        df = df[df["setup_cost"] == setup_cost]

        traces.append(go.Scatter(
            x=df['var'],
            y=df['j_value_function'],
            name="info_horizon = {0}, K={1}".format(information_horizon, str(setup_cost))
        )
        )
title = '<br>'.join(
    textwrap.wrap("Expected Optimal Cost, E[J(0, .)], Against Demand Variance at Constant Daily Expected Demand",
                  width=80)
)
layout = go.Layout(title=title,
                   xaxis={'title': 'Demand Variance'},
                   yaxis={'title': 'Optimal Expected Cost'})

figure = go.Figure(
    data=traces,
    layout=layout
)

plot(figure, filename="Expected_Cost_Against_Demand_Variance_for_Various_Info_Horizon_and_Setup_Cost.html")

line_styles = ("solid", "dot", "dash", "dashdot", "longdash", "longdashdot")
for setup_cost in set(summary["setup_cost"]):
    traces = []
    style_index = 0
    for information_horizon in set(summary["information_horizon"]):
        if information_horizon == 5:
            continue
        df = summary[summary["information_horizon"] == information_horizon]
        df = df[df["setup_cost"] == setup_cost]

        traces.append(
            go.Scatter(
                x=df['var'],
                y=df['j_value_function'],
                name="info_horizon = {0}, K={1}".format(information_horizon, str(setup_cost)),
                line=dict(dash=line_styles[style_index % 5])
            )
        )
        style_index += 1
    title = '<br>'.join(
        textwrap.wrap(
            "Expected Optimal Cost, E[J(0, .)], Against Demand Variance",
            width=80)
    )
    layout = go.Layout(title=title,
                       xaxis={'title': 'Demand Variance'},
                       yaxis={'title': 'Expected Cost E[J(0,*)]'})

    figure = go.Figure(
        data=traces,
        layout=layout
    )
    plot(figure, filename="Expected_Cost_Against_Demand_Variance_for_Paper_K={0}.html".format(str(setup_cost)))
