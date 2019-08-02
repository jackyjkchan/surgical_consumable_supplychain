"""
Procedure count distribution. Probability of a surgery having x procedures conditional on the there being n surgeries
that day.
"""

from scm_analytics import ScmAnalytics, Analytics
from scm_analytics.model.SurgeryModel import procedure_count_distribution
from scm_analytics.config import lhs_config
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

from os import path
import plotly.plotly as py
import plotly.graph_objs as go
import numpy as np
import datetime

case_service = "All"
analytics = ScmAnalytics.ScmAnalytics(lhs_config)

for case_service in set(analytics.surgery_df["case_service"]):

    case = {
        "dim": "case_service",
        "op": "==",
        "val": case_service
    }
    elec = {
        "dim": "urgent_elective",
        "op": "==",
        "val": "Elective"
    }

    surgery_df = Analytics.process_filters(analytics.surgery_df, filters=[case, elec])
    if len(surgery_df) < 1:
        continue

    # surgery_df = Analytics.process_filters(analytics.surgery_df, filters=[elec])
    surgery_df["is_weekday"] = surgery_df["start_date"].apply(lambda x: True if x.weekday() < 5 else False)
    surgery_df = surgery_df[surgery_df["is_weekday"]]
    surgery_df = surgery_df.drop_duplicates("event_id", keep="last")
    surgery_df = surgery_df[surgery_df["start_date"] > datetime.date(2016, 1, 1)]

    surgeries_per_day = surgery_df.groupby("start_date") \
        .agg({"event_id": "nunique"}) \
        .rename(columns={"event_id": "n_surgery_day"})

    surgery_df = surgery_df.join(surgeries_per_day,
                                 on="start_date",
                                 how="left",
                                 rsuffix="surgery_count")

    dist_df = procedure_count_distribution(surgery_df, group_by="n_surgery_day")
    total_dist = procedure_count_distribution(surgery_df)
    if total_dist:
        s = 1
        e = int(max(total_dist) + 1)

        total_trace = go.Histogram(
            x=total_dist,
            histnorm='probability',
            name='All Days, mean={0:0.2f}'.format(np.mean(total_dist)),
            xbins=dict(start=s, end=e, size=1),
            opacity=0.75
        )

        traces = [
            go.Histogram(
                x=dist_df.iloc[i]["data"],
                histnorm='probability',
                name='{0:d} Surgery Days, mean={1:0.2f} n_surgeries={2:d}'.format(int(dist_df.iloc[i]["n_surgery_day"]),
                                                                                  np.mean(dist_df.iloc[i]["data"]),
                                                                                  len(dist_df.iloc[i]["data"])),
                xbins=dict(start=s, end=e, size=1),
                opacity=0.75
            ) for i in range(len(dist_df))
        ]

        data = [total_trace] + traces

        title = 'Procedure Count Distribution of Elective {0} Surgeries Conditional on n Surgeries in Day'.format(
            case_service)
        fn = "procedure_count_distribution_{0}.html".format(case_service.replace("/", "_"))
        layout = go.Layout(
            title=title,
            xaxis=dict(
                title='Number of Procedures Per Surgery'
            ),
            yaxis=dict(
                title='Probability'
            ),
            bargap=0.2,
            bargroupgap=0.1
        )
        fig = go.Figure(data=data, layout=layout)
        plot(fig, filename=fn)
