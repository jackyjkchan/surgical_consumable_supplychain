import pandas as pd

fn = "scripts/optimization_model/results/batch_mdp_results_demand_x_usage_variance_20190920_merged.pickle"
data = pd.read_pickle(fn)
data = data[data["t"] == 15]

np = 5
p = {'Binomial p=5/9': 5 / 9,
     'Binomial p=5/20': 5 / 20,
     'Deterministic': 1,
     'Poisson': 0,
     'Binomial p=5/6': 5 / 6,
     'Binomial p=5/8': 5 / 8,
     'Binomial p=5/7': 5 / 7,
     'Binomial p=5/10': 5 / 10}

data["usage_variance"] = data["usage_model"].apply(lambda x: np * (1 - p[x]))
data["demand_variance"] = data["exogenous_label"].apply(lambda x: np * (1 - p[x]))

summary = data.groupby(["usage_variance",
                        "demand_variance",
                        "information_horizon"]
                       ).agg({"j_value_function": "mean"}).reset_index()
summary["id"] = summary.apply(lambda row: (row['usage_variance'], row['demand_variance']), axis=1)
summary = summary.pivot(index='id', columns='information_horizon', values="j_value_function").reset_index()
summary["discount"] = summary.apply(lambda row: (1-row[2]/row[0]), axis=1)
summary["usage_variance"] = summary.apply(lambda row: row["id"][0], axis=1)
summary["demand_variance"] = summary.apply(lambda row: row["id"][1], axis=1)
result = summary.pivot(index='demand_variance', columns='usage_variance', values="discount")
result.to_csv("cost_reduction_n_2_demand_vs_usage_variance.csv")