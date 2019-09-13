import pandas as pd
import numpy as np
import statsmodels.api as sm
import rpy2.robjects as robjects
import rpy2.robjects.numpy2ri

from rpy2.robjects import pandas2ri
from scm_analytics import ScmAnalytics, Analytics
from statsmodels.api import families
from rpy2.robjects.packages import importr

base = importr('base')
stats = importr('stats')
broom = importr('broom')

pandas2ri.activate()
robjects.numpy2ri.activate()


# 129636, 38242
def surgery_usage_regression_df(surgery_df, usage_df, item_ids=[], case_cart_df=None, filters=[], common_events=True):
    surgery_df = Analytics.process_filters(surgery_df, filters)
    surgery_df = surgery_df.drop_duplicates(subset=["event_id"])
    usage_df = Analytics.process_filters(usage_df, filters)
    if case_cart_df:
        case_cart_df = Analytics.process_filters(case_cart_df, filters)

    if common_events:
        surgery_df = surgery_df[surgery_df["event_id"].isin(set(usage_df["event_id"]))]

    # usage_df = usage_df[usage_df["item_id"].isin(item_ids)]
    # usage_df = usage_df.drop_duplicates(["event_id", "item_id"], keep="last")
    # usage_df = usage_df.pivot(index="event_id", columns="item_id", values="used_qty") \
    #                    .fillna(0) \
    #                    .reset_index()
    usage_df = usage_df.drop_duplicates(["event_id", "item_id"], keep="last")
    usage_df = surgery_df[surgery_df["event_id"].isin(set(usage_df["event_id"]))] \
        .join(usage_df[usage_df["item_id"].isin(item_ids)]
              .pivot(index="event_id", columns="item_id", values="used_qty"),
              on="event_id",
              how="left",
              rsuffix="item")\
        .fillna(0)

    procedure_df = pd.concat([pd.Series(row['event_id'], row['procedures']) for _, row in surgery_df.iterrows()],
                             ).reset_index().rename(columns={"index": "procedure",
                                                             0: "event_id"})
    procedure_df["flag"] = 1
    regression_df = procedure_df \
        .pivot(index="event_id", columns="procedure", values="flag") \
        .fillna(0) \
        .reset_index() \
        .join(usage_df.set_index("event_id"),
              on="event_id",
              how="left",
              rsuffix="usage")
    if common_events:
        regression_df[item_ids] = regression_df[item_ids].fillna(0)
    return regression_df


def extract_features(regression_df, features, all_procedures, interactions=[], other=False, sum_others=False):
    """
    :param regression_df:
    :param features: list of labels indicating which features to extract
    :param all_procedures: list of labels that are procedures
    :param interactions: list of sets of features to combine with AND operator as new feature
    :param other: Deprecated
    :param sum_others: Procedures that are not in a part of the set of features will be grouped together
    :return:
    """
    # print(interactions)
    added_interactions = []
    for interaction in interactions:
        p1, p2 = interaction
        regression_df[interaction] = \
            (regression_df[p2].astype(bool) & regression_df[p1].astype(bool)).astype(float)
        if sum(regression_df[interaction]) > 0:
            added_interactions.append(interaction)
    all_features = list(features) + added_interactions

    if sum_others:
        excluded = set(all_procedures) - set(features)
        regression_df["sum_others"] = regression_df.apply(lambda row: sum(row[i] for i in excluded),
                                                          axis=1)
        if sum(regression_df["sum_others"]) == 0:
            sum_others = False
    if sum_others:
        all_features += ["sum_others"]

    if other:
        excluded = set(all_procedures) - set(features)
        regression_df["other"] = regression_df.apply(lambda row: float(not (bool(sum(row[i] for i in features)))),
                                                     axis=1)
        if sum(regression_df["other"]) == 0:
            other = False
    if other:
        all_features += ["other"]

    X = np.array(regression_df[all_features].values.tolist())
    feature_df = pd.DataFrame()
    feature_df["feature"] = all_features
    feature_df["occurrence"] = feature_df["feature"].apply(lambda x: sum(regression_df[x]) if x in regression_df.columns
    else np.Inf)
    return X, feature_df


class Interaction(tuple):
    def __str__(self):
        return ".".join(self)


def extract_features_data(regression_df, features, all_procedures, interactions=[], other=False, sum_others=True):
    """
    :param regression_df:
    :param features: list of labels indicating which features to extract
    :param all_procedures: list of labels that are procedures
    :param interactions: list of sets of features to combine with AND operator as new feature
    :param other: Deprecated
    :param sum_others: Procedures that are not in a part of the set of features will be grouped together
    :return:
    """
    interactions = list(Interaction(i) for i in interactions)

    added_interactions = []
    for interaction in interactions:
        p1, p2 = interaction
        regression_df[str(interaction)] = \
            (regression_df[p2].astype(bool) & regression_df[p1].astype(bool)).astype(float)
        if sum(regression_df[str(interaction)]) > 0:
            added_interactions.append(str(interaction))
    all_features = list(features) + added_interactions

    if sum_others:
        excluded = set(all_procedures) - set(features)
        regression_df["sum_others"] = regression_df.apply(lambda row: sum(row[i] for i in excluded),
                                                          axis=1)
        if sum(regression_df["sum_others"]) > 0:
            all_features += ["sum_others"]

    if other:
        excluded = set(all_procedures) - set(features)
        regression_df["other"] = regression_df.apply(lambda row: float(not (bool(sum(row[i] for i in features)))),
                                                     axis=1)
        if sum(regression_df["other"]) > 0:
            all_features += ["other"]

    data = regression_df[all_features]
    feature_df = pd.DataFrame()
    feature_df["feature"] = all_features
    feature_df["occurrence"] = feature_df["feature"].apply(lambda x: sum(regression_df[x]) if x in regression_df.columns
    else np.Inf)

    return data, feature_df


def compute_rsquares(y, glm_results):
    y_bar = np.mean(y)
    ss_tot = sum((y_bar - y) ** 2)
    ss_res = sum((glm_results.fittedvalues - y) ** 2)
    r2 = 1 - ss_res / ss_tot
    return r2


def compute_rpy2_rsquares(y, fitted_y):
    y_bar = np.mean(y)
    ss_tot = sum((y_bar - y) ** 2)
    ss_res = sum((fitted_y - y) ** 2)
    r2 = 1 - ss_res / ss_tot
    return r2


def run_regression(x, y, feature_df, model=families.Gaussian()):
    # regression_results = sm.GLM(y, x, family=model).fit(maxiter=1000)
    # feature_df["pvalue"] = list(regression_results.pvalues)
    # feature_df["coefficient"] = list(regression_results.params)
    # r2 = compute_rsquares(y, regression_results)

    nr, nc = x.shape
    r_x = robjects.r.matrix(x, nrow=nr, ncol=nc)
    r_y = robjects.r.array(y)
    results = stats.glm_fit(r_x, r_y, family=stats.gaussian(), factors=feature_df["features"])
    fitted_y = list(stats.fitted(results))
    col_names = list(stats.summary_glm(results).rx2('coefficients').colnames)
    data = pandas2ri.ri2py(stats.summary_glm(results).rx2('coefficients'))

    dataset = pd.DataFrame({col_names[i]: data[:, i] for i in range(len(col_names))})

    r2 = compute_rpy2_rsquares(y, fitted_y)
    return feature_df, r2


def run_r_regression(data, feature_df, model="gaussian"):
    model = {
        "gaussian": stats.gaussian(),
        "poisson": stats.poisson()
    }[model]

    results = stats.glm("y ~ . -1", data=pandas2ri.py2ri(data), family=model)
    r = broom.tidy_lm(results)
    df = pd.DataFrame({name: np.asarray(r.rx(name))[0] for name in r.names})
    fitted_y = list(stats.fitted(results))
    col_names = list(stats.summary_glm(results).rx2('coefficients').colnames)

    feature_df = feature_df.join(df[["term", "estimate", "p.value"]].set_index("term"),
                                 on="feature",
                                 how="left",
                                 rsuffix="fit")
    r2 = compute_rpy2_rsquares(data["y"], fitted_y)
    return feature_df, r2, fitted_y
