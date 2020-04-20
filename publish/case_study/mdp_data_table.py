import pandas as pd

item_ids = ["47320", "56931", "1686", "129636", "83532", "38262"]

data0s = [pd.read_pickle(
    "scm_implementation/results/2020-01-22_ns_impl_{}.pickle".format(item_id)
) for item_id in item_ids]
data1s = [pd.read_pickle(
    "scm_implementation/results/2020-04-08_ns_impl_LT_1_{}.pickle".format(item_id)
) for item_id in item_ids]
datas = data1s + data0s
data = pd.concat(datas)

full_value_data0 = pd.read_csv("scm_implementation/results/2020-01-01_full_info_implementation_results.csv")
full_value_data0 = full_value_data0.rename(columns={"mean": "j_value_function_FULL"})
full_value_data0["item_id"] = full_value_data0["item_id"].apply(lambda x: str(x))

t = max(data["t"])
groupbys = ['item_id', 'usage_model', 'gamma', 'holding_cost',
            'backlogging_cost', 'setup_cost', 'unit_price', 'information_horizon',
            'lead_time', 'increments', "t"]
groupbys = groupbys + ["info_rv_str"] if "info_rv_str" in data else groupbys
data = data[(data["t"] == t)] if t else data
data = data[data["information_horizon"] < 3]
data["item_id"] = data["label"].apply(lambda x: x.split("_")[-1])
# data["information_horizon"] = data["info_state_rvs"].apply(lambda x:
#                                                            len(x) - 1 if len(x) > 2 else 1 if x[1].mean() else 0
#                                                            )

data = data[(data["inventory_position_state"] == 0)]
data = data[data["backlogging_cost"] > 100]
data["j_value_function"] = data["j_value_function"] * data["information_state_p"]
summary = data.groupby(groupbys).agg({"j_value_function": "sum"}).reset_index()
summary = summary[["backlogging_cost", "lead_time", "item_id", "information_horizon", "j_value_function"]]
summary["information_horizon"] = summary["information_horizon"].apply(lambda x: str(int(x)))

pivoted = summary.pivot_table(["j_value_function"],
                           ["item_id", "backlogging_cost", "lead_time"], ["information_horizon"])
pivoted.columns = pivoted.columns.to_series().str.join('_')
pivoted = pivoted.reset_index()
pivoted["value_ABI_1"] = 1 - pivoted["j_value_function_1"] / pivoted["j_value_function_0"]
pivoted["value_ABI_2"] = 1 - pivoted["j_value_function_2"] / pivoted["j_value_function_0"]

indices = ["item_id", "backlogging_cost", "lead_time"]
pivoted = pivoted.join(full_value_data0.set_index(indices), on=indices, how="left")
pivoted["F(1)"] = 1-pivoted["j_value_function_1"]/pivoted["j_value_function_0"]
pivoted["F(2)"] = 1-pivoted["j_value_function_1"]/pivoted["j_value_function_0"]
pivoted["F(infty)"] = 1-pivoted["j_value_function_FULL"]/pivoted["j_value_function_0"]
pivoted["F(infty) lower"] = 1-(pivoted["upper"])/pivoted["j_value_function_0"]
pivoted["F(infty) upper"] = 1-(pivoted["lower"])/pivoted["j_value_function_0"]

pivoted.to_csv("full_info_value_publish_table.csv")