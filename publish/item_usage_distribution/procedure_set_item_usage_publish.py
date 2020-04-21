from scm_analytics import ScmAnalytics, Analytics
from scm_analytics.model.SurgeryModel import procedure_count_distribution, surgeries_per_day_distribution, \
    pre_process_columns
from scm_analytics.config import lhs_config
import datetime
import plotly.graph_objs as go
from plotly.offline import plot
import numpy as np
import plotly

plotly.io.orca.config.executable = 'C:\\Users\\Jacky\\AppData\\Local\\Programs\\orca\\orca.exe'


def run(case_service="Cardiac Surgery",
        item_id="1686",
        procedure_set=None):
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
    surgery_df = surgery_df[surgery_df["procedures"] == procedure_set]

    traces = []

    x_max = int(max(surgery_df["used_qty"])) + 1

    data = surgery_df["used_qty"]
    label = ", ".join(procedure_set)
    fn = "__".join(procedure_set)
    fn = "Usage_Dist_item_" + item_id + "_" + fn.replace(" ", "_") + ".svg"

    traces.append(go.Histogram(
        x=data,
        name=label,
        xbins=dict(
            start=0,
            end=x_max,
            size=1
        ),
        histnorm='probability',
        opacity=0.75,

    ))

    tickvals = list(x + 0.5 for x in range(x_max))
    ticktext = list(str(x) for x in range(x_max))
    layout = go.Layout(  # title="Item: {} Empirical Usage Distribution for common cases".format(item_id),
        xaxis={'title': 'Used Qty',
               'tickvals': tickvals,
               'ticktext': ticktext},
        yaxis={'title': 'Probability'},
        font={"size": 16},
        plot_bgcolor="white",
        bargap=0.2)
    figure = go.Figure(
        data=traces,
        layout=layout,
    )
    # figure.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    figure.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
    # plot(figure, filename="{}_empircal_usage_distribution.html".format(item_id))
    figure.write_image(fn, width=900, height=600)


if __name__ == "__main__":
    # item_id = "47320"
    # procedure_sets = [frozenset({'cabg triple'}),
    #                   frozenset({'ita', 'esvh', 'cabg triple'})]
    # for procedure_set in procedure_sets:
    #     run(item_id=item_id,
    #         procedure_set=procedure_set)

    # item_id = "1686"
    # procedure_sets = [frozenset({'aortic valve'})]
    # for procedure_set in procedure_sets:
    #     run(item_id=item_id,
    #         procedure_set=procedure_set)

    procedure_set = frozenset({'superior vena cava cannulation', 'femoral cannulation', 'mitral valve repair mini thorocotomy'})
    run(item_id="38262",
        procedure_set=procedure_set)
