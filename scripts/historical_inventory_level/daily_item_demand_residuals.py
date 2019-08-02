import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import scipy.stats as stats

from itertools import combinations
from statsmodels.api import families

from scm_analytics import ScmAnalytics
from scm_analytics.model import SurgeryUsageRegressionModel as SURegressionModel
from scm_analytics.config import lhs_config
from scm_analytics.model.SurgeryUsageRegressionModel import Interaction

case_service = "Cardiac Surgery"
item_id = "129636"
weekday_only = False

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
surgery_df["real_usage"] = list(data["real_usage"])

start = min(surgery_df["start_date"])
end = max(surgery_df["start_date"])

day_df = pd.DataFrame()
day_df["day"] = pd.date_range(start=start, end=end, freq='D')
day_df["day"] = day_df["day"].apply(lambda x: x.date())
if weekday_only:
    day_df = day_df[day_df["day"].apply(lambda x: x.weekday() < 5)]

day_df = day_df.join(surgery_df.groupby(["start_date"]).agg({"real_usage": "sum",
                                                             "expected_usage": "sum"}),
                     on="day",
                     how="left",
                     rsuffix="usage").fillna(0)

poisson_model_residuals = day_df["expected_usage"] - day_df["real_usage"]
poisson_s = np.floor(min(poisson_model_residuals))-0.5
poisson_e = np.ceil(max(poisson_model_residuals))+0.5

default_model_residuals = np.mean(day_df["real_usage"]) - day_df["real_usage"]
default_s = np.floor(min(default_model_residuals))-0.5
default_e = np.ceil(max(default_model_residuals))+0.5


step = 1
traces = [
    go.Histogram(
        x=poisson_model_residuals,
        name='Poisson Residuals (Fit - Empirical)',
        xbins=dict(
            start=poisson_s,
            end=poisson_e,
            size=step
        ),
        histnorm='probability density',
        opacity=0.75
    ),
    go.Scatter(
        x=np.arange(poisson_s, poisson_e, 0.1),
        y=stats.norm.pdf(np.arange(poisson_s, poisson_e, 0.1),
                         np.mean(poisson_model_residuals),
                         np.std(poisson_model_residuals)),
        mode='lines',
        name='Poisson Model Daily Demand Residuals mu={0:.5f}, sigma={1:.2f}'.format(np.mean(poisson_model_residuals),
                                                                                     np.std(poisson_model_residuals)),
    ),
    go.Histogram(
        x=default_model_residuals,
        name='Default Daily Demand Model Residuals (Daily Mean - Empirical)',
        xbins=dict(
            start=default_s,
            end=default_e,
            size=step
        ),
        histnorm='probability density',
        opacity=0.75
    ),
    go.Scatter(
        x=np.arange(default_s, default_e, 0.1),
        y=stats.norm.pdf(np.arange(default_s, default_e, 0.1),
                         np.mean(default_model_residuals),
                         np.std(default_model_residuals)),
        mode='lines',
        name='Default Residuals, sigma={0:.2f}'.format(np.std(default_model_residuals)),
    )
]
title = "Estimated Daily Item Demand Residuals"
if weekday_only:
    title = "Estimated Daily Item Demand Residuals for Weekdays"

layout = go.Layout(title=title,
                   xaxis={'title': 'Residual'},
                   yaxis={'title': 'Probability Density'})
figure = go.Figure(
    data=traces,
    layout=layout
)
fn = "{0}_weekday_daily_item_demand_residuals.html".format(item_id) \
    if weekday_only else "{0}_daily_item_demand_residuals.html".format(item_id)

plot(figure, filename=fn)