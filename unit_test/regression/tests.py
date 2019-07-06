import pandas as pd
import os
import matplotlib.pyplot as plt
from itertools import combinations
from statsmodels.api import families

from scm_analytics import ScmAnalytics
from scm_analytics.model import SurgeryUsageRegressionModel as SURegressionModel
from scm_analytics.config import lhs_config


def test_surgery_usage_regression_df():
    case_service = "Cardiac Surgery"

    analytics = ScmAnalytics.ScmAnalytics(lhs_config)
    surgery_df = analytics.surgery_df
    usage_df = analytics.usage_df
    item_ids = ["38242", "129636"]

    surgery_df = surgery_df[surgery_df["case_service"] == case_service]
    usage_df = usage_df[usage_df["case_service"] == case_service]
    surgery_df = surgery_df[surgery_df["event_id"].isin(set(usage_df["event_id"]))]

    all_procedures = set.union(*surgery_df["procedures"])
    r_df = SURegressionModel.surgery_usage_regression_df(surgery_df,
                                                         usage_df,
                                                         item_ids=item_ids)

    # print(r_df.iloc[0])

    interactions = [("cabg double", "esvh"), ("ita", "esvh")]
    features = ["cabg double", "esvh", "ita", "cabg single"]

    # print(all_procedures)
    x, feature_df = SURegressionModel.extract_features(r_df, features, all_procedures, interactions)


def test_usage_r_regression_flow():
    from scm_analytics.model.SurgeryUsageRegressionModel import Interaction
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    pd.options.mode.chained_assignment = None

    case_service = "Cardiac Surgery"
    item_id = "38242"
    pthres = 0.05
    occ_thres = 5

    analytics = ScmAnalytics.ScmAnalytics(lhs_config)
    surgery_df = analytics.surgery_df
    usage_df = analytics.usage_df
    item_ids = ["38242", "129636"]

    surgery_df = surgery_df[surgery_df["case_service"] == case_service]
    usage_df = usage_df[usage_df["case_service"] == case_service]
    surgery_df = surgery_df[surgery_df["event_id"].isin(set(usage_df["event_id"]))]
    surgery_df["procedures"] = surgery_df["procedures"].apply(lambda x: set(e.replace(" ", "_") for e in x))

    all_procedures = set.union(*surgery_df["procedures"])
    r_df = SURegressionModel.surgery_usage_regression_df(surgery_df,
                                                         usage_df,
                                                         item_ids=item_ids)

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
        feature_df, r2 = SURegressionModel.run_r_regression(data, feature_df, model="gaussian")
        print(feature_df)
        print("r2:", r2)
        thres_df = feature_df[feature_df["feature"].isin(features+interactions)]
        if thres_df[thres_df["p.value"] > pthres].empty and thres_df[thres_df["occurrence"] < occ_thres].empty:
            break

        feature_df = feature_df[feature_df["p.value"] <= pthres]
        feature_df = feature_df[feature_df["occurrence"] >= occ_thres]
        interactions = list(filter(lambda x: str(x) in set(feature_df["feature"]), interactions))
        features = list(filter(lambda x: x in set(feature_df["feature"]), features))

    feature_df = feature_df[["feature", "occurrence"]]
    feature_df, r2 = SURegressionModel.run_r_regression(data, feature_df, model="poisson")
    feature_df.to_csv(os.path.join("regression_results", item_id), index=False)
    data.to_csv(os.path.join("r_scripts", "test_data2.csv"), index=False)
    print(feature_df)
    print("r2:", r2)


def test_rpy2():
    return


if __name__ == "__main__":
    # test_surgery_usage_regression_df()
    # test_usage_regression_flow()
    test_usage_r_regression_flow()
