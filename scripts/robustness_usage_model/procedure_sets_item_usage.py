from scm_analytics import ScmAnalytics, Analytics
from scm_analytics.model.SurgeryModel import procedure_count_distribution, surgeries_per_day_distribution, \
    pre_process_columns
from scm_analytics.config import lhs_config
import datetime
import plotly.graph_objs as go
from plotly.offline import plot
import numpy as np
import matplotlib.pyplot as plt

from scripts.usage_regression.usage_regression import CASE_STUDY_ITEMS, HIGH_USAGE_ITEMS, MED_USAGE_ITEMS, \
    LOW_USAGE_ITEMS


def run(case_service="Cardiac Surgery",
        item_id="1686"):
    analytics = ScmAnalytics.ScmAnalytics(lhs_config)
    case_service_filter = [{"dim": "case_service",
                            "op": "eq",
                            "val": case_service
                            }]

    usage_df = analytics.usage_df
    usage_df = usage_df[usage_df["start_date"].notna()]
    usage_df = Analytics.process_filters(usage_df, filters=case_service_filter)
    usage_events = set(usage_df["event_id"])
    item_usage_df = usage_df[usage_df["item_id"] == item_id]

    surgery_df = pre_process_columns(analytics.surgery_df)
    surgery_df = surgery_df[surgery_df["start_date"].notna()]
    surgery_df = surgery_df[surgery_df["start_date"] > datetime.date(2016, 1, 1)]
    surgery_df = Analytics.process_filters(surgery_df, filters=case_service_filter)
    surgery_df = surgery_df[surgery_df["event_id"].isin(usage_events)]

    surgery_df = surgery_df.join(item_usage_df.set_index("event_id")[["used_qty"]], on="event_id", how="left").fillna(0)
    surgery_df["procedures"] = surgery_df["procedures"].apply(lambda x: frozenset(x))

    usage_dist = surgery_df.groupby(["procedures"]).agg({"used_qty": lambda x: list(x)}).reset_index()
    usage_dist["occurrences"] = usage_dist["used_qty"].apply(lambda x: len(x))
    usage_dist = usage_dist[usage_dist["occurrences"] > 25]
    usage_dist["mean"] = usage_dist["used_qty"].apply(lambda x: np.mean(x))
    usage_dist["variance"] = usage_dist["used_qty"].apply(lambda x: np.var(x, ddof=1))
    usage_dist["var/mean"] = usage_dist["variance"] / usage_dist["mean"]

    df = surgery_df[surgery_df["procedures"].isin(usage_dist["procedures"])][["start_date", "used_qty"]]
    rolling_df = df[["used_qty"]].rolling(100).mean()
    plt.plot(list(rolling_df["used_qty"]))
    rolling_df = df[["used_qty"]].rolling(50).mean()
    plt.plot(list(rolling_df["used_qty"]))
    plt.savefig("{}_rolling_usage.png".format(item_id), format="png")

    traces = []
    x_max = 0
    for i in range(len(usage_dist)):
        case = usage_dist.iloc[i]["procedures"]
        data = usage_dist.iloc[i]["used_qty"]
        label = ", ".join(case)
        end = max(usage_dist.iloc[i]["used_qty"]) + 1
        traces.append(go.Histogram(
            x=data,
            name=label,
            xbins=dict(
                start=0,
                end=end,
                size=1
            ),
            histnorm='probability',
            opacity=0.75
        ))
        x_max = int(end) if end > x_max else x_max

    tickvals = list(x + 0.5 for x in range(x_max))
    ticktext = list(str(x) for x in range(x_max))
    layout = go.Layout(  # title="Item: {} Empirical Usage Distribution for common cases".format(item_id),
        xaxis={'title': 'Used Qty',
               'tickvals': tickvals,
               'ticktext': ticktext},
        yaxis={'title': 'Probability'},
        font={"size": 12},
        plot_bgcolor="white")
    figure = go.Figure(
        data=traces,
        layout=layout,
    )
    # figure.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    figure.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    plot(figure, filename="{}_empircal_usage_distribution.html".format(item_id))
    usage_dist.to_csv("{}_empircal_usage_distribution.csv".format(item_id))
    print(usage_dist["var/mean"].mean())

if __name__ == "__main__":
    item_id = "82099"
    run(item_id=item_id)
    # for item_id in CASE_STUDY_ITEMS:
    #    run(item_id=item_id)
