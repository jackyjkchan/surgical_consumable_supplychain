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


fn = 'scripts/optimization_model/results/batch_mdp_results_20190825_merged.pickle'
data = pd.read_pickle(fn)
traces = []

test_cases_var = {
    "E[Demand] 5": test_case_var([5]),
    "E[Demand] 3, 7": test_case_var([3, 7]),
    "E[Demand] 1, 9": test_case_var([1, 9]),
    "E[Demand] 0, 10": test_case_var([0, 10])
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
        summary['cost_percentage'] = summary['j_value_function'] / max(summary['j_value_function'])

        traces.append(go.Scatter(
            x=list(range(len(summary['information_horizon']))),
            y=summary['cost_percentage'],
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
plot(figure, filename="Expected_Cost_For_Various_Levels_of_Advanced_Information_Multi_K.html")