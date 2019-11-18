from scm_analytics import ScmAnalytics, Analytics
from scm_analytics.model.SurgeryModel import procedure_count_distribution, surgeries_per_day_distribution, \
    pre_process_columns
from scm_analytics.config import lhs_config
import datetime
import plotly.graph_objs as go
from plotly.offline import plot

from scripts.usage_regression.usage_regression import HIGH_USAGE_ITEMS, MED_USAGE_ITEMS, LOW_USAGE_ITEMS

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
    usage_dist = usage_dist[usage_dist["occurrences"] > 50]

    traces = []
    for i in range(len(usage_dist)):
        case = usage_dist.iloc[i]["procedures"]
        data = usage_dist.iloc[i]["used_qty"]
        label = ", ".join(case)

        traces.append(go.Histogram(
            x=data,
            name=label,
            xbins=dict(
                start=0,
                end=max(usage_dist.iloc[i]["used_qty"])+1,
                size=1
            ),
            histnorm='probability',
            opacity=0.75
        ))

    layout = go.Layout(title="Item: {} Empirical Usage Distribution for common cases".format(item_id),
                       xaxis={'title': 'Used Qty'},
                       yaxis={'title': 'Probability'})
    figure = go.Figure(
        data=traces,
        layout=layout
    )
    plot(figure, filename="{}_empircal_usage_distribution.html".format(item_id))


if __name__ == "__main__":
    for item_id in HIGH_USAGE_ITEMS + MED_USAGE_ITEMS:
        run(item_id=item_id)
