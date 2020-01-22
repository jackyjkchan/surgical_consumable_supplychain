import pandas as pd
import os
from itertools import combinations
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import plotly.graph_objs as go
from plotly.offline import plot

from scm_analytics import ScmAnalytics
from scm_analytics.config import lhs_config
from scm_analytics.model.SurgeryUsageRegressionModel import Interaction
from scm_analytics.model import SurgeryUsageRegressionModel as SURegressionModel

# usage > 1500 HIGH, > 500 MED, > 200 LOW
HIGH_USAGE_ITEMS = ["38242", "47320", "56931", "83104", "35893", "83106", "1686"]
MED_USAGE_ITEMS = ["35863", "80950", "40576", "81007", "129636", "83105", "38200", "39315", "7414", "120767",
                   "21685", "43940", "44696", "40585", "38246"]
LOW_USAGE_ITEMS = ["83532", "44748", "38238", "14205", "36551", "82916", "2997", "38247", "42317", "84382", "43954",
                   "38141", "38261", "38262", "36190"]
BAD_USAGE = ["62070", "382"]

# 129636, 1686, 44744, 38242 SUPER GOOD FOR POISSON


def test_usage_r_regression_flow(item_id=None, save_results=False):
    summary = {"item_id": item_id}

    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    pd.options.mode.chained_assignment = None

    case_service = "Cardiac Surgery"
    item_id = item_id if item_id else "38242"
    pthres = 0.05
    occ_thres = 8
    tail_trim = 0.01

    analytics = ScmAnalytics.ScmAnalytics(lhs_config)
    surgery_df = analytics.surgery_df
    usage_df = analytics.usage_df
    item_ids = [item_id]

    surgery_df = surgery_df[surgery_df["case_service"] == case_service]
    usage_df = usage_df[usage_df["case_service"] == case_service]

    surgery_df = surgery_df[surgery_df["event_id"].isin(set(usage_df["event_id"]))]
    surgery_df["procedures"] = surgery_df["procedures"].apply(lambda x: set(e.replace(" ", "_") for e in x))

    all_procedures = set.union(*surgery_df["procedures"])
    r_df = SURegressionModel.surgery_usage_regression_df(surgery_df,
                                                         usage_df,
                                                         item_ids=item_ids)

    if tail_trim:
        usage_df = usage_df[usage_df["item_id"] == item_id]
        trim_index = int(len(r_df) * (1 - tail_trim))
        expected_usage = np.mean(r_df[item_id])
        max_usage = max(r_df[item_id])
        usage_prob = len(usage_df)/len(surgery_df)

        trim_thres = r_df.sort_values(by=[item_id])[item_id].iloc[trim_index]
        discard_ratio = len(usage_df[usage_df["used_qty"] > trim_thres]) / len(usage_df)
        usage_df = usage_df[usage_df["used_qty"] <= trim_thres]

        print("Usage Probability:", usage_prob)
        print("Mean Usage:", expected_usage)
        print("Max Usage:", max_usage)
        print("Trim Threshold:", trim_thres)
        print("Discard Ratio:", discard_ratio)
        summary["usage_p"] = usage_prob
        summary["mean_usage"] = expected_usage
        summary["max_usage"] = max_usage
        summary["trim_thres"] = trim_thres
        summary["discard_ratio"] = discard_ratio


    interactions = list([Interaction((p1, p2)) for p1, p2 in combinations(sorted(list(all_procedures)), 2)])
    features = sorted(list(all_procedures))

    data, feature_df = SURegressionModel.extract_features_data(r_df,
                                                               features,
                                                               all_procedures,
                                                               interactions,
                                                               other=True,
                                                               sum_others=False)

    print(feature_df)
    feature_df = feature_df[feature_df["occurrence"] >= occ_thres]
    interactions = list(filter(lambda x: str(x) in set(feature_df["feature"]), interactions))
    features = list(filter(lambda x: x in set(feature_df["feature"]), features))

    while True:
        data, feature_df = SURegressionModel.extract_features_data(r_df,
                                                                   features,
                                                                   all_procedures,
                                                                   interactions,
                                                                   other=True,
                                                                   sum_others=False)
        data["y"] = list(r_df[item_id])
        feature_df, r2, _ = SURegressionModel.run_r_regression(data, feature_df, model="gaussian")
        print(feature_df)
        print("r2:", r2)
        thres_df = feature_df[feature_df["feature"].isin(features + interactions)]
        if thres_df[thres_df["p.value"] > pthres].empty and thres_df[thres_df["occurrence"] < occ_thres].empty:
            break

        feature_df = feature_df[feature_df["p.value"] <= pthres]
        feature_df = feature_df[feature_df["occurrence"] >= occ_thres]
        interactions = list(filter(lambda x: str(x) in set(feature_df["feature"]), interactions))
        features = list(filter(lambda x: x in set(feature_df["feature"]), features))

    feature_df = feature_df[["feature", "occurrence"]]
    feature_df, r2, fitted_y = SURegressionModel.run_r_regression(data, feature_df, model="poisson")
    residuals = fitted_y - data["y"]
    constant_residuals = np.mean(data["y"]) - data["y"]
    feature_df.to_csv(os.path.join("regression_results", item_id), index=False)
    data.to_csv(os.path.join("r_scripts", "test_data2.csv"), index=False)
    print(feature_df)
    print("r2:", r2)
    summary["r2"] = r2
    step = 0.5
    s = np.floor(min(residuals)) - step / 2
    e = np.ceil(max(residuals)) + step / 2

    mu = np.mean(residuals)
    std = np.std(residuals, ddof=1)
    bins = np.arange(s, e, step)
    norm_x = np.arange(s, e, step / 10)
    weights = np.ones(len(residuals)) / len(residuals)

    traces = [
        go.Histogram(
            x=residuals,
            name='Poisson Residuals (Fit - Empirical)',
            xbins=dict(
                start=s,
                end=e,
                size=step
            ),
            histnorm='probability density',
            opacity=0.75
        ),
        go.Scatter(
            x=norm_x,
            y=stats.norm.pdf(norm_x, mu, std),
            mode='lines',
            name='Poisson Residuals mu={0:.5f}, sigma={1:.2f}'.format(mu, std),
        ),
        go.Histogram(
            x=constant_residuals,
            name='Constant Model Residuals (Fit - Empirical)',
            xbins=dict(
                start=s,
                end=e,
                size=step
            ),
            histnorm='probability density',
            opacity=0.75
        ),
        go.Scatter(
            x=norm_x,
            y=stats.norm.pdf(norm_x, 0, np.std(data["y"], ddof=1)),
            mode='lines',
            name='Constant Residuals, sigma={0:.2f}'.format(np.std(data["y"], ddof=1)),
        )
    ]
    layout = go.Layout(title="Residuals", xaxis={'title': 'Residual'}, yaxis={'title': 'Probability Density'})
    figure = go.Figure(
        data=traces,
        layout=layout
    )
    plot(figure, filename="{0}_residuals_r2_{1:0.2f}.html".format(item_id, r2))

    plt.hist(residuals, bins=bins, density=True, rwidth=0.96, alpha=0.5, label="Residuals 'fit - empirical'")
    plt.plot(norm_x, stats.norm.pdf(norm_x, mu, std), label="mu={0:.5f}, sigma={1:.2f}".format(mu, std))
    plt.title("Residuals Histogram from Regression Model")
    plt.ylabel("Probability Density")
    plt.xlabel("Residual")
    plt.legend()
    if save_results:
        plt.savefig("{0}_surgery_item_usage_residuals_r2_{1:0.2f}.png".format(item_id, r2), format="png")
    #plt.show()
    return summary


if __name__ == "__main__":
    run_summary = pd.DataFrame()
    for id in HIGH_USAGE_ITEMS + MED_USAGE_ITEMS + LOW_USAGE_ITEMS:
       print("ITEM ID:", id)
       row = test_usage_r_regression_flow(item_id=id, save_results=True)
       run_summary = run_summary.append(row, ignore_index=True)
    print(run_summary)
