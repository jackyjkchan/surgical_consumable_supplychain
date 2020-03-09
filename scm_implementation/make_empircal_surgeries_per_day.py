from scm_simulation.hospital import Hospital, SurgeryDemandProcess
from scm_simulation.item import Item
from scm_simulation.surgery import Surgery
from scm_simulation.rng_classes import GeneratePoisson, GenerateFromSample, GenerateDeterministic
from scm_simulation.order_policy import AdvancedInfoSsPolicy
import pandas as pd
import os
import numpy as np
import pickle

import plotly.graph_objs as go
from plotly.offline import plot

from scm_analytics.model import SurgeryUsageRegressionModel as SURegressionModel
from scm_analytics.model.SurgeryUsageRegressionModel import Interaction
from scm_analytics.model.SurgeryModel import procedure_count_distribution, surgeries_per_day_distribution, \
    pre_process_columns
from scripts.usage_regression.usage_regression import HIGH_USAGE_ITEMS, MED_USAGE_ITEMS, LOW_USAGE_ITEMS
from scm_analytics import ScmAnalytics, Analytics
from scm_analytics.config import lhs_config
import datetime

analytics = ScmAnalytics.ScmAnalytics(lhs_config)
case_service = "Cardiac Surgery"
case_service_filter = [{"dim": "case_service",
                        "op": "eq",
                        "val": case_service
                        }]
usage_events = set(analytics.usage_df["event_id"])
surgery_df = surgery_df = Analytics \
    .process_filters(analytics.surgery_df,
                     filters=case_service_filter) \
    .drop_duplicates("event_id", keep="last")
surgery_df = surgery_df[surgery_df["event_id"].isin(usage_events)].sort_values(by="start_date")
surgery_df["weekday"] = surgery_df["start_date"].apply(lambda x: x.isoweekday() - 1)
start = surgery_df[surgery_df["weekday"] == 0].iloc[0]["start_date"]
surgery_df = surgery_df[surgery_df["start_date"] >= start]

surgery_df["day_index"] = surgery_df["start_date"].apply(lambda x: (x - start).days)
surgery_df = surgery_df[surgery_df["day_index"] < 365]

historical_elective_schedule = [[] for _ in range(365)]
historical_emergency_schedule = [[] for _ in range(365)]

day = pd.DataFrame()
day["day_index"] = list(range(0, 365))
df = surgery_df[surgery_df["urgent_elective"] == "Elective"] \
    .groupby("day_index") \
    .agg({"event_id": "nunique"}) \
    .reset_index()
day = day.join(df.set_index("day_index"),
               on="day_index",
               how="left").fillna(0)
day = day[day["day_index"].apply(lambda x: (x % 7) not in [5, 6])]
empirical_elective_surgeries_per_day = [int(x) for x in list(day["event_id"])]
with open("scm_implementation/simulation_inputs/empirical_elective_surgery_distribution.pickle", "wb") as f:
    pickle.dump(empirical_elective_surgeries_per_day, f)

day = pd.DataFrame()
day["day_index"] = list(range(0, 365))
df = surgery_df[surgery_df["urgent_elective"] == "Urgent"] \
    .groupby("day_index") \
    .agg({"event_id": "nunique"}) \
    .reset_index()
day = day.join(df.set_index("day_index"),
               on="day_index",
               how="left").fillna(0)
empirical_emergency_surgeries_per_day = [int(x) for x in list(day["event_id"])]
with open("scm_implementation/simulation_inputs/empirical_emergency_surgery_distribution.pickle", "wb") as f:
    pickle.dump(empirical_emergency_surgeries_per_day, f)
