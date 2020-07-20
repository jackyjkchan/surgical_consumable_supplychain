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
from scm_simulation.rng_classes import GenerateDeterministic
from scm_analytics.model import SurgeryUsageRegressionModel as SURegressionModel
from scm_analytics.model.SurgeryUsageRegressionModel import Interaction
from scm_analytics.model.SurgeryModel import procedure_count_distribution, surgeries_per_day_distribution, \
    pre_process_columns
from scripts.usage_regression.usage_regression import HIGH_USAGE_ITEMS, MED_USAGE_ITEMS, LOW_USAGE_ITEMS
from scm_analytics import ScmAnalytics, Analytics
from scm_analytics.config import lhs_config
import datetime

item_ids = ["47320", "56931", "1686", "129636", "83532", "38262", "83105", "83106", "21920", "38197", "82099"]
case_service = "Cardiac Surgery"
#item_id = "47320"
analytics = ScmAnalytics.ScmAnalytics(lhs_config)

case_service_filter = [{"dim": "case_service",
                        "op": "eq",
                        "val": case_service
                        }]

usage_events = set(analytics.usage_df["event_id"])
surgery_df = analytics.surgery_df[analytics.surgery_df["event_id"].isin(usage_events)]
surgery_df = Analytics.process_filters(surgery_df, filters=case_service_filter)
surgery_df["procedures"] = surgery_df["procedures"].apply(lambda x: set(e.replace(" ", "_") for e in x))
surgery_df = surgery_df.drop_duplicates("event_id", keep="last")
extracted_surgery_df = surgery_df[["event_id"]]

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

for item_id in item_ids:
    feature_df = pd.read_csv(os.path.join("regression_results", item_id))
    features = feature_df["feature"]
    featured_procedures = list(filter(lambda x: "." not in x, feature_df["feature"]))
    if "other" in featured_procedures:
        featured_procedures.remove("other")
    coeff = np.array(feature_df["estimate"])

    interactions = list(filter(lambda x: "." in x, feature_df["feature"]))
    interactions = list(Interaction(i.split(".")) for i in interactions)

    data, _ = SURegressionModel.extract_features_data(empirical_surgeries_df,
                                                      featured_procedures,
                                                      [],
                                                      interactions,
                                                      other=True)

    empirical_surgeries_df["feature_vector"] = data[features].values.tolist()

    usage_df = analytics.usage_df[analytics.usage_df["item_id"] == item_id]
    usage_df = usage_df.drop_duplicates("event_id", keep="last")

    extracted_surgery_df["{}_info".format(item_id)] = list(
        empirical_surgeries_df["feature_vector"].apply(lambda x: np.exp(np.dot(x, coeff)))
    )
    extracted_surgery_df["{}_historical".format(item_id)] = list(extracted_surgery_df.join(
        usage_df[["event_id", "used_qty"]].set_index("event_id"),
        on="event_id",
        rsuffix='_other').fillna(0)["used_qty"])

surgery_objects = list(
    extracted_surgery_df.apply(
        lambda row:
        Surgery(row["event_id"],
                {iid: row["{}_info".format(iid)] for iid in item_ids},
                {iid: GenerateDeterministic(row["{}_historical".format(iid)]) for iid in item_ids}),
        axis=1))
surgery_objects = {surgery.id: surgery for surgery in surgery_objects}
with open("scm_implementation/simulation_inputs/historical_surgeries.pickle", "wb") as f:
    pickle.dump(surgery_objects, f)
