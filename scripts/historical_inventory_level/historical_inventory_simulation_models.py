import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

from itertools import combinations
from statsmodels.api import families

from scm_analytics import ScmAnalytics
from scm_analytics.model import SurgeryUsageRegressionModel as SURegressionModel
from scm_analytics.config import lhs_config
from scm_analytics.model.SurgeryUsageRegressionModel import Interaction


def historical_inventory_level(day_df, initial_inventory):
    historical_day_df = day_df[["day"]]
    historical_day_df["change"] = day_df["received_qty"] - day_df["real_usage"]
    historical_day_df["inventory_level"] = historical_day_df["change"].cumsum()
    historical_day_df["inventory_level"] = historical_day_df["inventory_level"] + initial_inventory
    return historical_day_df["inventory_level"]


def empirical_inventory_level(day_df, surgery_df, gen, initial_inventory):
    surgery_df = surgery_df[["start_date", "procedures"]]
    surgery_df["usage"] = surgery_df["procedures"].apply(lambda p: gen(p))
    empirical_day_df = day_df.join(surgery_df.groupby(["start_date"]).agg({"usage": "sum"}),
                                   on="day",
                                   how="left",
                                   rsuffix="usage").fillna(0)
    empirical_day_df["change"] = day_df["received_qty"] - empirical_day_df["usage"]
    empirical_day_df["inventory_level"] = empirical_day_df["change"].cumsum()
    empirical_day_df["inventory_level"] = empirical_day_df["inventory_level"] + initial_inventory
    return empirical_day_df["inventory_level"]


def regression_inventory_level(day_df, surgery_df, initial_inventory):
    surgery_df = surgery_df[["start_date", "expected_usage"]]
    surgery_df["usage"] = surgery_df["expected_usage"].apply(lambda x: np.random.poisson(x))
    regres_day_df = day_df.join(surgery_df.groupby(["start_date"]).agg({"usage": "sum"}),
                                on="day",
                                how="left",
                                rsuffix="usage").fillna(0)

    regres_day_df["change"] = day_df["received_qty"] - regres_day_df["usage"]
    regres_day_df["inventory_level"] = regres_day_df["change"].cumsum()
    regres_day_df["inventory_level"] = regres_day_df["inventory_level"] + initial_inventory
    return regres_day_df["inventory_level"]


def regression_gap_fill_inventory_level(day_df, surgery_df, initial_inventory):
    choices = surgery_df[surgery_df["real_usage"].notna()]["real_usage"]
    surgery_df["usage"] = surgery_df.apply(lambda row:
                                           #np.random.choice(choices)
                                           np.random.poisson(row["expected_usage"])
                                           if np.isnan(row["real_usage"])
                                           else row["real_usage"],
                                           axis=1)
    gap_fill_day_df = day_df.join(surgery_df.groupby(["start_date"]).agg({"usage": "sum"}),
                                on="day",
                                how="left",
                                rsuffix="usage").fillna(0)

    gap_fill_day_df["change"] = day_df["received_qty"] - gap_fill_day_df["usage"]
    gap_fill_day_df["inventory_level"] = gap_fill_day_df["change"].cumsum()
    gap_fill_day_df["inventory_level"] = gap_fill_day_df["inventory_level"] + initial_inventory
    return gap_fill_day_df["inventory_level"]


def default_surgery_model_inventory_level(day_df, surgery_df, initial_inventory):
    surgery_df["usage"] = surgery_df["event_id"].apply(lambda x: np.random.choice(surgery_df["real_usage"]))
    def_model = day_df.join(surgery_df.groupby(["start_date"]).agg({"usage": "sum"}),
                            on="day",
                            how="left",
                            rsuffix="usage").fillna(0)

    def_model["change"] = day_df["received_qty"] - def_model["usage"]
    def_model["inventory_level"] = def_model["change"].cumsum()
    def_model["inventory_level"] = def_model["inventory_level"] + initial_inventory
    return def_model["inventory_level"]


def default_demand_model_inventory_level(day_df, initial_inventory):
    default_day_df = day_df[["day"]]
    usages = list(day_df["real_usage"])
    default_day_df["real_usage"] = list(np.random.choice(usages) for i in range(len(default_day_df)))
    default_day_df["change"] = day_df["received_qty"] - default_day_df["real_usage"]
    default_day_df["inventory_level"] = default_day_df["change"].cumsum()
    default_day_df["inventory_level"] = default_day_df["inventory_level"] + initial_inventory
    return default_day_df["inventory_level"]


case_service = "Cardiac Surgery"
item_id = "129636"
trials = 1

analytics = ScmAnalytics.ScmAnalytics(lhs_config)
surgery_df = analytics.surgery_df
usage_df = analytics.usage_df
item_ids = [item_id]

surgery_df = surgery_df[surgery_df["case_service"] == case_service]
surgery_df = surgery_df.drop_duplicates("event_id", keep="last")
usage_df = usage_df[usage_df["case_service"] == case_service]
surgery_df = surgery_df[surgery_df["event_id"].isin(set(usage_df["event_id"]))]
surgery_df["procedures"] = surgery_df["procedures"].apply(lambda x: set(e.replace(" ", "_") for e in x))

all_procedures = set.union(*surgery_df["procedures"])
r_df = SURegressionModel.surgery_usage_regression_df(surgery_df,
                                                     usage_df,
                                                     item_ids=item_ids)

feature_df = pd.read_csv(os.path.join("regression_results", item_id))
features = feature_df["feature"]
procedures = list(filter(lambda x: "." not in x, feature_df["feature"]))
if "other" in procedures:
    procedures.remove("other")
interactions = list(filter(lambda x: "." in x, feature_df["feature"]))
interactions = list(Interaction(i.split(".")) for i in interactions)

data, _ = SURegressionModel.extract_features_data(r_df,
                                                  procedures,
                                                  all_procedures,
                                                  interactions,
                                                  other=True,
                                                  sum_others=False)
coeff = np.array(feature_df["estimate"])
data["real_usage"] = r_df[item_id]
data["expected_usage"] = data[features].values.tolist()
data["expected_usage"] = data["expected_usage"].apply(lambda x: np.array(x))
data["expected_usage"] = data["expected_usage"].apply(lambda x: np.exp(np.dot(x, coeff)))

surgery_df["expected_usage"] = list(data["expected_usage"])

surgery_df["procedures"] = surgery_df["procedures"].apply(lambda x: frozenset(x))
surgery_df["real_usage"] = list(data["real_usage"])
empirical_dist = surgery_df.groupby("procedures").apply(lambda df: list(df["real_usage"])).to_dict()


def gen_empirical(procedures):
    return np.random.choice(empirical_dist[frozenset(procedures)])


surgery_df["start_date"] = surgery_df["start_dt"].apply(lambda x: x.date())
start = min(surgery_df["start_date"])
end = max(surgery_df["start_date"])

po_df = analytics.po_df
po_df = po_df[po_df["item_id"] == item_id]
po_df["delivery_date"] = po_df["delivery_date"].apply(lambda x: x.date())
po_df = po_df[po_df["delivery_date"] >= start]
po_df = po_df[po_df["delivery_date"] <= end]

day_df = pd.DataFrame()
day_df["day"] = pd.date_range(start=start, end=end, freq='D')
day_df["day"] = day_df["day"].apply(lambda x: x.date())

day_df = day_df.join(surgery_df.groupby(["start_date"]).agg({"real_usage": "sum"}),
                     on="day",
                     how="left",
                     rsuffix="usage").fillna(0)

day_df["received_qty"] = day_df.join(po_df.groupby(["delivery_date"]).agg({"qty_ea": "sum"}),
                                     on="day",
                                     how="left",
                                     rsuffix="delivery").fillna(0)["qty_ea"]

hist_df = day_df[["day"]]
hist_df[0] = historical_inventory_level(day_df, 20)

empirical_df = day_df[["day"]]
for i in range(trials):
    empirical_df[i] = empirical_inventory_level(day_df, surgery_df, gen_empirical, 20)

reg_df = day_df[["day"]]
for i in range(trials):
    reg_df[i] = regression_inventory_level(day_df, surgery_df, 20)

default_model = day_df[["day"]]
for i in range(trials):
    default_model[i] = default_surgery_model_inventory_level(day_df, surgery_df, 20)

default_day_model = day_df[["day"]]
for i in range(trials):
    default_day_model[i] = default_demand_model_inventory_level(day_df, 20)

#
# plt.step(hist_df["day"],
#          hist_df[0],
#          label="Historical")
# plt.step(empirical_df["day"],
#          empirical_df.apply(lambda row: np.mean([row[i] for i in range(trials)]), axis=1),
#          label="Empirical Model")
# plt.step(reg_df["day"],
#          reg_df.apply(lambda row: np.mean([row[i] for i in range(trials)]), axis=1),
#          label="Poisson Model")
# plt.step(default_model["day"],
#          default_model.apply(lambda row: np.mean([row[i] for i in range(trials)]), axis=1),
#          label="Default Model")

historical_trace = go.Scatter(
    x=empirical_df["day"],
    y=hist_df[0],
    mode='lines+markers',
    name="'Historical'",
    line=dict(shape='hv', color='rgb(31, 119, 180)'),
    marker=dict(color='rgb(31, 119, 180)')
)

empirical_df["mean"] = empirical_df.apply(lambda row: np.mean([row[i] for i in range(trials)]), axis=1)
empirical_df["5th"] = empirical_df.apply(lambda row: sorted([row[i] for i in range(trials)])[int(trials*0.05)], axis=1)
empirical_df["95th"] = empirical_df.apply(lambda row: sorted([row[i] for i in range(trials)])[int(trials*0.95)], axis=1)
empirical_trace = go.Scatter(
    x=empirical_df["day"],
    y=empirical_df["mean"],
    mode='lines+markers',
    name="'Empirical'",
    line=dict(shape='hv', color='rgb(255, 127, 14)'),
    marker=dict(color='rgb(255, 127, 14)')
)
empirical_conf_trace = go.Scatter(
    x=empirical_df["day"],
    y=empirical_df["mean"],
    error_y=dict(
            type='data',
            symmetric=False,
            array=empirical_df["95th"]-empirical_df["mean"],
            arrayminus=empirical_df["mean"]-empirical_df["5th"]
        ),
    mode='markers',
    name="'Empirical 5% and 95%'",
    marker=dict(color='rgb(255, 127, 14)')
)

reg_df["mean"] = reg_df.apply(lambda row: np.mean([row[i] for i in range(trials)]), axis=1)
reg_df["5th"] = reg_df.apply(lambda row: sorted([row[i] for i in range(trials)])[int(trials*0.05)], axis=1)
reg_df["95th"] = reg_df.apply(lambda row: sorted([row[i] for i in range(trials)])[int(trials*0.95)], axis=1)
poisson_trace = go.Scatter(
    x=empirical_df["day"],
    y=reg_df["mean"],
    mode='lines+markers',
    name="'Poisson'",
    line=dict(shape='hv', color='rgb(44, 160, 44)'),
    marker=dict(color='rgb(44, 160, 44)')
)
poisson_conf_trace = go.Scatter(
    x=reg_df["day"],
    y=reg_df["mean"],
    error_y=dict(
            type='data',
            symmetric=False,
            array=reg_df["95th"]-reg_df["mean"],
            arrayminus=reg_df["mean"]-reg_df["5th"]
        ),
    mode='markers',
    name="'Poisson 5% and 95%'",
    marker=dict(color='rgb(44, 160, 44)')
)

default_model["mean"] = default_model.apply(
    lambda row: np.mean([row[i] for i in range(trials)]),
    axis=1)
default_model["5th"] = default_model.apply(
    lambda row: sorted([row[i] for i in range(trials)])[int(trials*0.05)],
    axis=1)
default_model["95th"] = default_model.apply(
    lambda row: sorted([row[i] for i in range(trials)])[int(trials*0.95)],
    axis=1)
default_surgery_trace = go.Scatter(
    x=empirical_df["day"],
    y=default_model["mean"],
    mode='lines+markers',
    name="'Default Surgery'",
    line=dict(shape='hv', color='rgb(214, 39, 40)'),
    marker=dict(color='rgb(214, 39, 40)')
)
default_surgery_conf_trace = go.Scatter(
    x=reg_df["day"],
    y=reg_df["mean"],
    error_y=dict(
            type='data',
            symmetric=False,
            array=default_model["95th"]-default_model["mean"],
            arrayminus=default_model["mean"]-default_model["5th"]
        ),
    mode='markers',
    name="'Default Surgery 5% and 95%'",
    marker=dict(color='rgb(214, 39, 40)')
)


default_day_model["mean"] = default_day_model.apply(
    lambda row: np.mean([row[i] for i in range(trials)]),
    axis=1)
default_day_model["5th"] = default_day_model.apply(
    lambda row: sorted([row[i] for i in range(trials)])[int(trials*0.05)],
    axis=1)
default_day_model["95th"] = default_day_model.apply(
    lambda row: sorted([row[i] for i in range(trials)])[int(trials*0.95)],
    axis=1)
default_day_trace = go.Scatter(
    x=empirical_df["day"],
    y=default_day_model["mean"],
    mode='lines+markers',
    name="'Default Day'",
    line=dict(shape='hv', color='rgb(148, 103, 189)'),
    marker=dict(color='rgb(148, 103, 189)')
)
default_day_conf_trace = go.Scatter(
    x=reg_df["day"],
    y=reg_df["mean"],
    error_y=dict(
            type='data',
            symmetric=False,
            array=default_day_model["95th"]-default_day_model["mean"],
            arrayminus=default_day_model["mean"]-default_day_model["5th"]
        ),
    mode='markers',
    name="'Default Day 5% and 95%'",
    marker=dict(color='rgb(148, 103, 189)')
)
layout = go.Layout(title="Inventory Level Trace", xaxis={'title': 'Time'}, yaxis={'title': 'Inventory Level'})

figure = go.Figure(
    data=[historical_trace,
          empirical_trace,
          empirical_conf_trace,
          poisson_trace,
          poisson_conf_trace,
          default_surgery_trace,
          default_surgery_conf_trace,
          default_day_trace,
          default_day_conf_trace],
    layout=layout
)

plot(figure, filename=item_id+"_Inventory_Level_Trace.html")

#historical inventory with gap filling
trials = 1000

analytics = ScmAnalytics.ScmAnalytics(lhs_config)
surgery_df = analytics.surgery_df
usage_df = analytics.usage_df
item_ids = [item_id]

surgery_df = surgery_df[surgery_df["case_service"] == case_service]
surgery_df = surgery_df.drop_duplicates("event_id", keep="last")
surgery_df["start_date"] = surgery_df["start_dt"].apply(lambda x: x.date())
usage_df = usage_df[usage_df["case_service"] == case_service]
start, end = min(usage_df["start_date"]), max(usage_df["start_date"])
surgery_df["procedures"] = surgery_df["procedures"].apply(lambda x: set(e.replace(" ", "_") for e in x))
surgery_df = surgery_df[surgery_df["start_date"] >= start]
surgery_df = surgery_df[surgery_df["start_date"] <= end]


r_df = SURegressionModel.surgery_usage_regression_df(surgery_df,
                                                     usage_df,
                                                     item_ids=item_ids,
                                                     common_events=False)
data, _ = SURegressionModel.extract_features_data(r_df,
                                                  procedures,
                                                  all_procedures,
                                                  interactions,
                                                  other=True,
                                                  sum_others=False)
coeff = np.array(feature_df["estimate"])
data["real_usage"] = list(r_df[item_id])
data["expected_usage"] = data[features].values.tolist()
data["expected_usage"] = data["expected_usage"].apply(lambda x: np.array(x))
data["expected_usage"] = data["expected_usage"].apply(lambda x: np.exp(np.dot(x, coeff)))
data["start_date"] = list(surgery_df["start_date"])

gap_fill_df = day_df[["day"]]
for i in range(trials):
    gap_fill_df[i] = regression_gap_fill_inventory_level(day_df, data, 20)
gap_fill_df["mean"] = gap_fill_df.apply(lambda row: np.mean([row[i] for i in range(trials)]), axis=1)
gap_fill_df["5th"] = gap_fill_df.apply(lambda row: sorted([row[i] for i in range(trials)])[int(trials*0.05)], axis=1)
gap_fill_df["95th"] = gap_fill_df.apply(lambda row: sorted([row[i] for i in range(trials)])[int(trials*0.95)], axis=1)
gap_fill_trace = go.Scatter(
    x=gap_fill_df["day"],
    y=gap_fill_df["mean"],
    mode='lines+markers',
    name="'Poisson Gap Filling Model'",
    line=dict(shape='hv', color='rgb(255, 127, 14)'),
    marker=dict(color='rgb(255, 127, 14)')
)
gap_fill_conf_trace = go.Scatter(
    x=gap_fill_df["day"],
    y=gap_fill_df["mean"],
    error_y=dict(
            type='data',
            symmetric=False,
            array=gap_fill_df["95th"]-gap_fill_df["mean"],
            arrayminus=gap_fill_df["mean"]-gap_fill_df["5th"]
        ),
    mode='markers',
    name="'Poisson Model 5% and 95%'",
    marker=dict(color='rgb(255, 127, 14)')
)
layout = go.Layout(title="Inventory Level Trace With Usage Data Gap Filling", xaxis={'title': 'Time'}, yaxis={'title': 'Inventory Level'})

figure = go.Figure(
    data=[historical_trace,
          gap_fill_trace,
          gap_fill_conf_trace],
    layout=layout
)
plot(figure, filename=item_id+"_Inventory_Level_Trace_Gap_Filling.html")
