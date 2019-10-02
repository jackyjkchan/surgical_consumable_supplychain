import pandas as pd
import os
import pacal
import numpy as np

import matplotlib.pyplot as plt
import scipy.stats as st
import statsmodels.datasets

import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

from scm_analytics.model.SurgeryModel import procedure_count_distribution, surgeries_per_day_distribution, \
    pre_process_columns
from scm_analytics import ScmAnalytics, Analytics
from scm_analytics.config import lhs_config
import datetime

case_service = "Cardiac Surgery"
item_id = "38242"

analytics = ScmAnalytics.ScmAnalytics(lhs_config)

surgery_df = pre_process_columns(analytics.surgery_df)
surgery_df = surgery_df[surgery_df["start_date"].notna()]
surgery_df = surgery_df[surgery_df["start_date"] > datetime.date(2016, 1, 1)]

filters = [{"dim": "case_service",
            "op": "eq",
            "val": case_service
            },
           {"dim": "urgent_elective",
            "op": "eq",
            "val": "Elective"
            }]
case_service_filter = [{"dim": "case_service",
                        "op": "eq",
                        "val": case_service
                        }]

surgery_df = Analytics.process_filters(surgery_df, filters=filters)
dist_df = surgeries_per_day_distribution(surgery_df, day_group_by="is_weekday", filters=filters)
data = dist_df.set_index("is_weekday").loc[True]["data"]
bins = range(1 + int(max(data)))
binom_x = [x + 0.5 for x in bins]
n = int(max(data))
p = np.mean(data) / n

surgery_df["procedure_count"] = surgery_df["procedures"].apply(lambda x: len(x))
procedure_count_df = surgery_df.groupby("procedure_count").agg({"event_id": "count"}).reset_index()
procedure_count_df = procedure_count_df[procedure_count_df["procedure_count"] != 6]
procedure_count_df["p"] = procedure_count_df["procedure_count"] / sum(procedure_count_df["procedure_count"])

procedure_count_rv = pacal.DiscreteDistr(procedure_count_df["procedure_count"], procedure_count_df["p"])

"""
Procedure weights
"""
usage_events = set(analytics.usage_df["event_id"])
surgery_df = analytics.surgery_df[analytics.surgery_df["event_id"].isin(usage_events)]
surgery_df = Analytics.process_filters(surgery_df, filters=case_service_filter)
surgery_df["procedures"] = surgery_df["procedures"].apply(lambda x: set(e.replace(" ", "_") for e in x))
procedures = surgery_df["procedures"].apply(lambda x: list(x)).to_list()
procedures = pd \
    .DataFrame({"procedure": [val for sublist in procedures for val in sublist],
                "count": [1 for sublist in procedures for val in sublist]}) \
    .groupby("procedure") \
    .agg({"count": "count"}) \
    .reset_index()

procedures["p"] = procedures["count"] / sum(procedures["count"])
#procedures["procedure"] = procedures["procedure"].apply(lambda x: x.replace(" ", "_"))


def procedure_pick_rv(size):
    return np.random.choice(procedures["procedure"], p=procedures["p"], replace=False, size=size)


synthetic_surgeries = pd.DataFrame({"event_id": list(range(1000))})
synthetic_surgeries["procedure_count"] = procedure_count_rv.rand(1000)
synthetic_surgeries["procedures"] = synthetic_surgeries["procedure_count"].apply(lambda x: procedure_pick_rv(x))

synthetic_procedure_df = pd.concat(
    [pd.Series(row['event_id'], row['procedures']) for _, row in synthetic_surgeries.iterrows()]) \
    .reset_index() \
    .rename(columns={"index": "procedure",
                     0: "event_id"}
            )
synthetic_procedure_df["flag"] = 1
synthetic_surgeries_df = synthetic_procedure_df \
    .pivot(index="event_id", columns="procedure", values="flag") \
    .fillna(0) \
    .reset_index()

from scm_analytics.model import SurgeryUsageRegressionModel as SURegressionModel
from scm_analytics.model.SurgeryUsageRegressionModel import Interaction

feature_df = pd.read_csv(os.path.join("regression_results", item_id))
features = feature_df["feature"]
featured_procedures = list(filter(lambda x: "." not in x, feature_df["feature"]))
if "other" in featured_procedures:
    featured_procedures.remove("other")
for fp in featured_procedures:
    if fp not in synthetic_surgeries_df:
        print(procedures.set_index("procedure").loc[fp])
        synthetic_surgeries_df[fp] = 0

all_procedures = set.union(*surgery_df["procedures"])

interactions = list(filter(lambda x: "." in x, feature_df["feature"]))
interactions = list(Interaction(i.split(".")) for i in interactions)
data, _ = SURegressionModel.extract_features_data(synthetic_surgeries_df,
                                                  featured_procedures,
                                                  [],
                                                  interactions,
                                                  other=True)

for f in feature_df["feature"]:
    if f not in data:
        print(f)
        data[f] = 0
synthetic_surgeries_df["feature_vector"] = data[features].values.tolist()
coeff = np.array(feature_df["estimate"])
synthetic_surgeries_df["expected_usage"] = synthetic_surgeries_df["feature_vector"]\
    .apply(lambda x: np.exp(np.dot(x, coeff)))


"""
Information rv for empirical surgeries
"""
surgery_df = surgery_df.drop_duplicates("event_id", keep="last")
empirical_procedure_df = pd.concat(
    [pd.Series(row['event_id'], row['procedures']) for _, row in surgery_df.iterrows()]) \
    .reset_index() \
    .rename(columns={"index": "procedure",
                     0: "event_id"}
            )
empirical_procedure_df["flag"] = 1
empirical_surgeries_df = empirical_procedure_df \
    .pivot(index="event_id", columns="procedure", values="flag") \
    .fillna(0) \
    .reset_index()
data, _ = SURegressionModel.extract_features_data(empirical_surgeries_df,
                                                  featured_procedures,
                                                  [],
                                                  interactions,
                                                  other=True)
empirical_surgeries_df["feature_vector"] = data[features].values.tolist()
empirical_surgeries_df["expected_usage"] = empirical_surgeries_df["feature_vector"]\
    .apply(lambda x: np.exp(np.dot(x, coeff)))

"""
Plotly histogram for 
"""
s = 0
e = int(max(max(empirical_surgeries_df["expected_usage"]), max(synthetic_surgeries_df["expected_usage"]))+1)
empirical_trace = go.Histogram(
            x=empirical_surgeries_df["expected_usage"],
            name='Empirical Surgery Info RV (mean={:0.2f})'.format(np.mean(empirical_surgeries_df["expected_usage"])),
            xbins=dict(
                start=s,
                end=e,
                size=0.5
            ),
            histnorm='probability density',
            opacity=0.75
        )
synthetic_trace = go.Histogram(
            x=synthetic_surgeries_df["expected_usage"],
            name='Synthetic Surgery Info RV (mean={:0.2f})'.format(np.mean(synthetic_surgeries_df["expected_usage"])),
            xbins=dict(
                start=s,
                end=e,
                size=0.5
            ),
            histnorm='probability density',
            opacity=0.75
        )
layout = go.Layout(title="Per Surgery Info R.V Item: {0}".format(item_id),
                   xaxis={'title': 'Info [Expected Usage]'},
                   yaxis={'title': 'Probability Density'})
figure = go.Figure(
        data=[empirical_trace, synthetic_trace],
        layout=layout
    )
plot(figure, filename="{0}_Per_Surgery_Info_Rv.html".format(item_id))