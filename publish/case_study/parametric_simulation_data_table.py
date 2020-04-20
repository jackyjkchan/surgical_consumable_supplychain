import pandas as pd
import numpy as np

data = pd.read_csv("publish/case_study/2020-04-15_parametric_case_study_results_500.csv")
data["cost"] = data["average_inventory_level"] * 365 + data["surgeries_backlogged"] * data["backlogging_cost"]
data["info_horizon"] = data["info_horizon"].apply(lambda x: str(int(x)))

pivoted = data.pivot_table(["average_inventory_level", "surgeries_backlogged", "service_level", "cost"],
                           ["item_id", "backlogging_cost", "lead_time", "seed"], ["info_horizon"])
pivoted.columns = pivoted.columns.to_series().str.join('_')
pivoted = pivoted.reset_index()

pivoted["delta_service_level_1"] = pivoted["service_level_1"] - pivoted["service_level_0"]
pivoted["delta_service_level_2"] = pivoted["service_level_2"] - pivoted["service_level_0"]

pivoted["inv_reduced_1"] = 1 - pivoted["average_inventory_level_1"] / pivoted["average_inventory_level_0"]
pivoted["inv_reduced_2"] = 1 - pivoted["average_inventory_level_2"] / pivoted["average_inventory_level_0"]

pivoted["value_1"] = 1 - pivoted["cost_1"] / pivoted["cost_0"]
pivoted["value_2"] = 1 - pivoted["cost_2"] / pivoted["cost_0"]


def halfwidth(series):
    return 1.96 * np.std(series) / np.sqrt(len(series))


methods = ["mean", halfwidth]
summary = pivoted.groupby(["backlogging_cost", "lead_time", "item_id"]) \
    .agg({
    "average_inventory_level_0": methods,
    "average_inventory_level_1": methods,
    "average_inventory_level_2": methods,
    "surgeries_backlogged_0": methods,
    "surgeries_backlogged_1": methods,
    "surgeries_backlogged_2": methods,
    "service_level_0": methods,
    "service_level_1": methods,
    "service_level_2": methods,
    "delta_service_level_1": methods,
    "delta_service_level_2": methods,
    "cost_0": methods,
    "cost_1": methods,
    "cost_2": methods,
    "value_1": methods,
    "value_2": methods,
    "inv_reduced_1": methods,
    "inv_reduced_2": methods}
)

publish_col = ["average_inventory_level_0",
               "average_inventory_level_1",
               "average_inventory_level_2",
               "surgeries_backlogged_0",
               "surgeries_backlogged_1",
               "surgeries_backlogged_2",
               "service_level_0",
               "service_level_1",
               "service_level_2",
               "inv_reduced_1",
               "inv_reduced_2"
               ]

summary.to_csv("publish/case_study/2020-04-15_parametric_case_study_truncated_publish_table.csv")
