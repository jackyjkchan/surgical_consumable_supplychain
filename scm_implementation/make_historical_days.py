from scm_simulation.hospital import Hospital, SurgeryDemandProcess
from scm_simulation.item import Item
from scm_simulation.surgery import Surgery
from scm_simulation.rng_classes import GeneratePoisson, GenerateFromSample, GenerateDeterministic
from scm_simulation.order_policy import AdvancedInfoSsPolicy
import pandas as pd
import os
import pacal
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

with open("scm_implementation/simulation_inputs/historical_surgeries.pickle", "rb") as f:
    surgery_objects = pickle.load(f)

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
surgery_df["weekday"] = surgery_df["start_date"].apply(lambda x: x.isoweekday()-1)
start = surgery_df[surgery_df["weekday"] == 0].iloc[0]["start_date"]
surgery_df = surgery_df[surgery_df["start_date"] >= start]

surgery_df["day_index"] = surgery_df["start_date"].apply(lambda x: (x - start).days)
surgery_df = surgery_df[surgery_df["day_index"] < 365]

historical_elective_schedule = [[] for _ in range(365)]
historical_emergency_schedule = [[] for _ in range(365)]

for i in range(len(surgery_df)):
    event_id = surgery_df.iloc[i]["event_id"]
    is_emergency = bool(surgery_df.iloc[i]["urgent_elective"] == "Urgent")
    day_index = surgery_df.iloc[i]["day_index"]
    if is_emergency:
        historical_emergency_schedule[day_index].append(surgery_objects[event_id])
    else:
        historical_elective_schedule[day_index].append(surgery_objects[event_id])

with open("scm_implementation/simulation_inputs/historical_elective_schedule.pickle", "wb") as f:
    pickle.dump(historical_elective_schedule, f)

with open("scm_implementation/simulation_inputs/historical_emergency_schedule.pickle", "wb") as f:
    pickle.dump(historical_emergency_schedule, f)
