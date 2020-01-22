import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st
from statistics import mode
from pprint import pprint

from scm_analytics.model.SurgeryModel import surgeries_per_day_distribution, pre_process_columns
from scm_analytics import ScmAnalytics
from scm_analytics.config import lhs_config
import datetime

case_service = "Cardiac Surgery"

statistics = {}

analytics = ScmAnalytics.ScmAnalytics(lhs_config)
surgery_df = pre_process_columns(analytics.surgery_df)
surgery_df = surgery_df[surgery_df["start_date"].notna()]
surgery_df = surgery_df[surgery_df["start_date"] > datetime.date(2016, 1, 1)]
surgery_df = surgery_df[surgery_df["start_date"] < datetime.date(2017, 1, 1)]
surgery_df = surgery_df[surgery_df["case_service"] == case_service]
surgery_df["num_procedures"] = surgery_df["procedures"].apply(lambda x: len(x))

usage_df = analytics.usage_df
usage_df = usage_df[usage_df["case_service"] == case_service]


statistics["total surgeries performed (2016 cardiac)"] = len(surgery_df)
statistics["number different procedures (2016 cardiac)"] = len(set().union(*list(surgery_df["procedures"])))
statistics["number different surgeries (2016 cardiac)"] = len(set(surgery_df["procedures"].apply(lambda x: tuple(x))))
statistics["total procedures performed (2016 cardiac)"] = sum(surgery_df["num_procedures"])
statistics["procedures per surgery (min, mode, max)"] = (min(surgery_df["num_procedures"]),
                                                         mode(surgery_df["num_procedures"]),
                                                         max(surgery_df["num_procedures"]))
statistics["procedures per surgery (mean)"] = np.mean(surgery_df["num_procedures"])
statistics["number of different items (cardiac)"] = len(set(usage_df["item_id"]))
statistics["total items consumed (cardiac)"] = int(sum(usage_df["used_qty"]))
statistics["total cost of items consumed (cardiac)"] = int(sum(usage_df["used_qty"] * usage_df["unit_price"]))

pprint(statistics)
