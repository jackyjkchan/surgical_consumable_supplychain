import pandas as pd
import numpy as np

item_ids = ["1686", "21920", "38197", "47320", "82099"]
data = pd.read_csv("publish/case_study/2020-04-15_parametric_case_study_results_500.csv")
data_catheter = pd.read_pickle("publish/case_study/2020-04-23_parametric_case_study_catheters.pickle")
data_round3 = pd.read_pickle("publish/case_study/2020-07-24_parametric_case_study_round3.pickle")
data_b100 = pd.read_pickle("publish/case_study/2020-08-01_parametric_case_study_b_100.pickle")
data = pd.concat([data, data_round3, data_b100], sort=False)
data["item_id"] = data["item_id"].apply(lambda x: str(x))
data = data[data["item_id"].isin(item_ids)]

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

summary.to_csv("publish/case_study/2020-08-01_parametric_case_study_truncated_publish_table.csv")

summary["backlogging_cost"] = summary["backlogging_cost"].apply(lambda x: str(x))
summary["lead_time"] = summary["lead_time"].apply(lambda x: str(x))

publish = summary.reset_index()[["item_id", "backlogging_cost", "lead_time"]]
publish["backlogging_cost"] = publish["backlogging_cost"].apply(lambda x: "{0:0.0f}".format(x))
publish["lead_time"] = publish["lead_time"].apply(lambda x: "{0:0.0f}".format(x))

publish["0-ABI Inv Level"] = summary.reset_index().apply(
    lambda x: "{0:0.2f}".format(x["average_inventory_level_0"]["mean"]), axis=1)

publish["1-ABI Inv Level"] = summary.reset_index().apply(
    lambda x: "{0:0.2f} ({1:0.2f}\%)".format(x["average_inventory_level_1"]["mean"],
                                           100*x["inv_reduced_1"]["mean"]), axis=1)
publish["2-ABI Inv Level"] = summary.reset_index().apply(
    lambda x: "{0:0.2f} ({1:0.2f}\%)".format(x["average_inventory_level_2"]["mean"],
                                           100*x["inv_reduced_2"]["mean"]), axis=1)

publish["0-ABI Service Level"] = summary.reset_index().apply(
    lambda x: "{0:0.3f}".format(100*x["service_level_0"]["mean"]), axis=1)

publish["delta 1-ABI Service Level"] = summary.reset_index().apply(
    lambda x: "{0:0.3f}".format(100*x["delta_service_level_1"]["mean"]), axis=1)
publish["delta 2-ABI Service Level"] = summary.reset_index().apply(
    lambda x: "{0:0.3f}".format(100*x["delta_service_level_2"]["mean"]), axis=1)
publish = publish.sort_values(by=["item_id", "backlogging_cost", "lead_time"])

publish_CI = publish[["item_id", "backlogging_cost", "lead_time"]]
publish_CI["0-ABI Inv Level"] = summary.reset_index().apply(
    lambda x: "$\pm{0:0.2f}$".format(x["average_inventory_level_0"]["halfwidth"]), axis=1)

publish_CI["1-ABI Inv Level"] = summary.reset_index().apply(
    lambda x: "$\pm{0:0.2f} ({1:0.2f}pp)$".format(x["average_inventory_level_1"]["halfwidth"],
                                           100*x["inv_reduced_1"]["halfwidth"]), axis=1)
publish_CI["2-ABI Inv Level"] = summary.reset_index().apply(
    lambda x: "$\pm{0:0.2f} ({1:0.2f}pp)$".format(x["average_inventory_level_2"]["halfwidth"],
                                           100*x["inv_reduced_2"]["halfwidth"]), axis=1)

publish_CI["0-ABI Service Level"] = summary.reset_index().apply(
    lambda x: "$\pm{0:0.3f}pp$".format(100*x["service_level_0"]["halfwidth"]), axis=1)

publish_CI["delta 1-ABI Service Level"] = summary.reset_index().apply(
    lambda x: "$\pm{0:0.3f}pp$".format(100*x["delta_service_level_1"]["halfwidth"]), axis=1)
publish_CI["delta 2-ABI Service Level"] = summary.reset_index().apply(
    lambda x: "$\pm{0:0.3f}pp$".format(100*x["delta_service_level_2"]["halfwidth"]), axis=1)
publish_CI = publish_CI.sort_values(by=["item_id", "backlogging_cost", "lead_time"])

with open("publish/case_study/2020-08-01_parametric_case_study_truncated_publish_table.txt", "w") as f:
    for i in range(len(publish_CI)):
        f.write("\t\t&".join(publish.iloc[i].to_list()) + "\t \\\\ \n")
        f.write("\t\t&".join(publish_CI.iloc[i].to_list()) + "\t \\\\ \n")
