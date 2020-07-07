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


def boostrap_info_process(item_id="38242"):
    case_service = "Cardiac Surgery"
    #item_id = "3824ns_info_state_rvs2"
    info_granularity = 1
    eps_trunk = 1e-3

    elective_outdir = "scm_implementation/ns_info_state_rvs/elective"
    emergency_outdir = "scm_implementation/ns_info_state_rvs/emergency"

    analytics = ScmAnalytics.ScmAnalytics(lhs_config)

    filters = [{"dim": "case_service",
                "op": "eq",
                "val": case_service
                },
               {"dim": "urgent_elective",
                "op": "eq",
                "val": "Elective"
                }]
    elective_filter = [{"dim": "urgent_elective",
                        "op": "eq",
                        "val": "Elective"
                        }]
    emergency_filter = [{"dim": "urgent_elective",
                         "op": "eq",
                         "val": "Urgent"
                         }]
    case_service_filter = [{"dim": "case_service",
                            "op": "eq",
                            "val": case_service
                            }]

    surgery_df = pre_process_columns(analytics.surgery_df)
    surgery_df = surgery_df[surgery_df["start_date"].notna()]
    surgery_df = surgery_df[surgery_df["start_date"] > datetime.date(2016, 1, 1)]
    surgery_df = Analytics.process_filters(surgery_df, filters=elective_filter + case_service_filter)
    dist_df = surgeries_per_day_distribution(surgery_df, day_group_by="is_weekday", filters=[])
    data = dist_df.set_index("is_weekday").loc[True]["data"]
    bins = range(1 + int(max(data)))
    binom_x = [x + 0.5 for x in bins]
    n = int(max(data))
    p = np.mean(data) / n

    surgery_df = pre_process_columns(analytics.surgery_df)
    surgery_df = surgery_df[surgery_df["start_date"].notna()]
    surgery_df = surgery_df[surgery_df["start_date"] > datetime.date(2016, 1, 1)]
    surgery_df = Analytics.process_filters(surgery_df, filters=emergency_filter + case_service_filter)
    dist_df = surgeries_per_day_distribution(surgery_df, filters=[])
    emergency_surgeries_mean = np.mean(dist_df)

    surgery_df = Analytics.process_filters(analytics.surgery_df, filters=case_service_filter)
    surgery_df["procedure_count"] = surgery_df["procedures"].apply(lambda x: len(x))
    procedure_count_df = surgery_df.groupby("procedure_count").agg({"event_id": "count"}).reset_index()
    procedure_count_df = procedure_count_df[procedure_count_df["procedure_count"] != 6]
    procedure_count_df["p"] = procedure_count_df["procedure_count"] / sum(procedure_count_df["procedure_count"])
    procedure_count_rv = pacal.DiscreteDistr(procedure_count_df["procedure_count"], procedure_count_df["p"])

    """
    Procedure weights
    """
    usage_events = set(analytics.usage_df["event_id"])
    surgery_df = analytics.surgery_df[analytics.surgery_df["event_id"].isin(usage_events)]
    surgery_df = Analytics.process_filters(surgery_df, filters=case_service_filter)
    surgery_df["procedures"] = surgery_df["procedures"].apply(lambda x: set(e.replace(" ", "_") for e in x))
    procedures = surgery_df["procedures"].apply(lambda x: list(x)).to_list()
    procedures = pd \
        .DataFrame({"procedure": [val for sublist in procedures for val in sublist],
                    "count": [1 for sublist in procedures for val in sublist]}) \
        .groupby("procedure") \
        .agg({"count": "count"}) \
        .reset_index()

    procedures["p"] = procedures["count"] / sum(procedures["count"])

    def procedure_pick_rv(size):
        return np.random.choice(procedures["procedure"], p=procedures["p"], replace=False, size=size)

    synthetic_surgeries = pd.DataFrame({"event_id": list(range(1000))})
    synthetic_surgeries["procedure_count"] = procedure_count_rv.rand(1000)
    synthetic_surgeries["procedures"] = synthetic_surgeries["procedure_count"].apply(lambda x: procedure_pick_rv(x))

    synthetic_procedure_df = pd.concat(
        [pd.Series(row['event_id'], row['procedures']) for _, row in synthetic_surgeries.iterrows()]) \
        .reset_index() \
        .rename(columns={"index": "procedure",
                         0: "event_id"}
                )
    synthetic_procedure_df["flag"] = 1
    synthetic_surgeries_df = synthetic_procedure_df \
        .pivot(index="event_id", columns="procedure", values="flag") \
        .fillna(0) \
        .reset_index()

    feature_df = pd.read_csv(os.path.join("regression_results", item_id))
    features = feature_df["feature"]
    featured_procedures = list(filter(lambda x: "." not in x, feature_df["feature"]))
    if "other" in featured_procedures:
        featured_procedures.remove("other")
    for fp in featured_procedures:
        if fp not in synthetic_surgeries_df:
            print(procedures.set_index("procedure").loc[fp])
            synthetic_surgeries_df[fp] = 0

    all_procedures = set.union(*surgery_df["procedures"])

    interactions = list(filter(lambda x: "." in x, feature_df["feature"]))
    interactions = list(Interaction(i.split(".")) for i in interactions)
    data, _ = SURegressionModel.extract_features_data(synthetic_surgeries_df,
                                                      featured_procedures,
                                                      [],
                                                      interactions,
                                                      other=True)

    for f in feature_df["feature"]:
        if f not in data:
            print(f)
            data[f] = 0
    synthetic_surgeries_df["feature_vector"] = data[features].values.tolist()
    coeff = np.array(feature_df["estimate"])
    synthetic_surgeries_df["expected_usage"] = synthetic_surgeries_df["feature_vector"] \
        .apply(lambda x: np.exp(np.dot(x, coeff)))

    """
    Information rv for empirical surgeries
    """
    surgery_df = surgery_df.drop_duplicates("event_id", keep="last")
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
    data, _ = SURegressionModel.extract_features_data(empirical_surgeries_df,
                                                      featured_procedures,
                                                      [],
                                                      interactions,
                                                      other=True)
    empirical_surgeries_df["feature_vector"] = data[features].values.tolist()
    empirical_surgeries_df["expected_usage"] = empirical_surgeries_df["feature_vector"] \
        .apply(lambda x: np.exp(np.dot(x, coeff)))

    """
    Plotly histogram for per surgery info rv, empirical surgeries and synthetic using regression results 
    """
    s = 0
    e = int(max(max(empirical_surgeries_df["expected_usage"]), max(synthetic_surgeries_df["expected_usage"])) + 1)
    empirical_trace = go.Histogram(
        x=empirical_surgeries_df["expected_usage"],
        name='Empirical Surgery Info RV (mean={:0.2f})'.format(np.mean(empirical_surgeries_df["expected_usage"])),
        xbins=dict(
            start=s,
            end=e,
            size=info_granularity
        ),
        histnorm='probability density',
        opacity=0.75
    )
    synthetic_trace = go.Histogram(
        x=synthetic_surgeries_df["expected_usage"],
        name='Synthetic Surgery Info RV (mean={:0.2f})'.format(np.mean(synthetic_surgeries_df["expected_usage"])),
        xbins=dict(
            start=s,
            end=e,
            size=info_granularity
        ),
        histnorm='probability density',
        opacity=0.75
    )
    layout = go.Layout(title="Per Surgery Info R.V Item: {0}".format(item_id),
                       xaxis={'title': 'Info [Expected Usage]'},
                       yaxis={'title': 'Probability Density'})
    figure = go.Figure(
        data=[empirical_trace, synthetic_trace],
        layout=layout
    )
    plot(figure, filename="{0}_Per_Surgery_Info_Rv.html".format(item_id))

    """
    Plotly histogram for per weekday elective surgery RV
    """
    empirical_rv_df = empirical_surgeries_df.groupby(["expected_usage"]) \
        .agg({"event_id": "count"}) \
        .rename(columns={"event_id": "count"}) \
        .reset_index()
    empirical_rv_df["p"] = empirical_rv_df["count"] / sum(empirical_rv_df["count"])
    emp_surgery_rv = pacal.DiscreteDistr(empirical_rv_df["expected_usage"],
                                         empirical_rv_df["p"])
    surgery_demand_rv = pacal.BinomialDistr(n, p)
    days = 100000
    elective_samples = [sum(emp_surgery_rv.rand(x)) for x in np.random.binomial(n, p, days)]
    elective_samples = [round(sample / info_granularity) * info_granularity for sample in elective_samples]
    weekday_elective_trace = go.Histogram(
        x=elective_samples,
        name='{} Elective Info RV (mean={:0.2f})'.format(item_id, np.mean(elective_samples)),
        xbins=dict(
            start=0,
            end=max(elective_samples),
            size=info_granularity
        ),
        histnorm='probability',
        opacity=0.75
    )
    """
    Plotly histogram for per day emergency surgery RV
    """
    emergency_samples = [sum(emp_surgery_rv.rand(x)) for x in np.random.poisson(emergency_surgeries_mean, days)]
    emergency_samples = [round(sample / info_granularity) * info_granularity for sample in emergency_samples]
    emergency_trace = go.Histogram(
        x=emergency_samples,
        name='{} Emergency Info RV (mean={:0.2f})'.format(item_id, np.mean(emergency_samples)),
        xbins=dict(
            start=0,
            end=max(emergency_samples),
            size=info_granularity
        ),
        histnorm='probability',
        opacity=0.75
    )
    layout = go.Layout(title="Weekday Elective Info R.V Item: {0}".format(item_id),
                       xaxis={'title': 'Info State (Poisson Usage)]'},
                       yaxis={'title': 'Probability'})
    figure = go.Figure(
        data=[weekday_elective_trace, emergency_trace],
        layout=layout
    )
    plot(figure, filename="{0}_Weekday_Elective_Info_Rv.html".format(item_id))

    elective_info_df = pd.DataFrame({"info": elective_samples, "count": [1] * len(elective_samples)}) \
        .groupby(["info"]) \
        .agg({"count": "count"}) \
        .reset_index()
    elective_info_df["p"] = elective_info_df["count"] / sum(elective_info_df["count"])
    elective_info_rv = pacal.DiscreteDistr(elective_info_df["info"], elective_info_df["p"])

    emergency_info_df = pd.DataFrame({"info": emergency_samples, "count": [1] * len(emergency_samples)}) \
        .groupby(["info"]) \
        .agg({"count": "count"}) \
        .reset_index()
    emergency_info_df["p"] = emergency_info_df["count"] / sum(emergency_info_df["count"])
    emergency_info_rv = pacal.DiscreteDistr(emergency_info_df["info"], emergency_info_df["p"])

    max_v = 999
    for d in elective_info_rv.get_piecewise_pdf().getDiracs():
        if 1 - elective_info_rv.cdf(d.a) < eps_trunk:
            max_v = d.a
            break
    diracs = (pacal.CondLtDistr(elective_info_rv, max_v)) \
        .get_piecewise_pdf().getDiracs()
    diracs = list(filter(lambda d: d.f > 0, diracs))
    elective_info_rv = pacal.DiscreteDistr([d.a for d in diracs], [d.f for d in diracs])

    max_v = 999
    for d in emergency_info_rv.get_piecewise_pdf().getDiracs():
        if 1 - emergency_info_rv.cdf(d.a) < eps_trunk:
            max_v = d.a
            break
    diracs = (pacal.CondLtDistr(emergency_info_rv, max_v)) \
        .get_piecewise_pdf().getDiracs()
    diracs = list(filter(lambda d: d.f > 0, diracs))
    emergency_info_rv = pacal.DiscreteDistr([d.a for d in diracs], [d.f for d in diracs])

    with open(os.path.join(elective_outdir, "{0}.pickle".format(item_id)), "wb") as f:
        pickle.dump(elective_info_rv, f)

    with open(os.path.join(emergency_outdir, "{0}.pickle".format(item_id)), "wb") as f:
        pickle.dump(emergency_info_rv, f)

    return emergency_trace, weekday_elective_trace


if __name__ == "__main__":
    emergency_traces = []
    weekday_elective_traces = []
    selected_items = ["38242", "47320", "56931", "1686", "129636", "83532", "38262", "83105", "83106"]
    selected_items = ["83105", "83106"]
    for item_id in selected_items: #HIGH_USAGE_ITEMS + MED_USAGE_ITEMS + LOW_USAGE_ITEMS:
        print(item_id)
        emergency_trace, weekday_elective_trace = boostrap_info_process(item_id=item_id)
        emergency_traces.append(emergency_trace)
        weekday_elective_traces.append(weekday_elective_trace)


    layout = go.Layout(title="Weekday Elective Info R.V - High Usage",
                       xaxis={'title': 'Info State (Poisson Usage)]'},
                       yaxis={'title': 'Probability'})
    figure = go.Figure(
        data=weekday_elective_traces,
        layout=layout
    )
    plot(figure, filename="Weekday_Elective_Info_Rv_High.html")

    layout = go.Layout(title="Emergency Info R.V - High Usage",
                       xaxis={'title': 'Info State (Poisson Usage)]'},
                       yaxis={'title': 'Probability'})
    figure = go.Figure(
        data=emergency_traces,
        layout=layout
    )
    plot(figure, filename="Emergency_Info_Rv_High.html")
