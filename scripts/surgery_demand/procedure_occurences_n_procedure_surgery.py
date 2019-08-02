from scm_analytics import ScmAnalytics, Analytics
from scm_analytics.model.SurgeryModel import procedure_count_distribution
from scm_analytics.config import lhs_config
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

from os import path
import plotly.plotly as py
import plotly.graph_objs as go
import numpy as np
import pandas as pd
from pandas import Series

case_service = "Cardiac Surgery"
analytics = ScmAnalytics.ScmAnalytics(lhs_config)

case = {
    "dim": "case_service",
    "op": "==",
    "val": case_service
}

surgery_df = Analytics.process_filters(analytics.surgery_df, filters=[case])

usage_events = set(analytics.usage_df["event_id"])
usage_procedures = set.union(*list(surgery_df[surgery_df["event_id"].isin(usage_events)]["procedures"]))
# surgery_df = surgery_df[surgery_df["event_id"].isin(usage_events)]
surgery_df = surgery_df[surgery_df["procedures"].apply(lambda x: True if x.issubset(usage_procedures) else False)]

surgery_df["procedure_count"] = surgery_df["procedures"].apply(lambda x: len(x))

procedure_df = pd.concat([Series(row['event_id'], row['procedures']) for _, row in surgery_df.iterrows()]) \
    .reset_index() \
    .rename(columns={"index": "procedure", 0: "event_id"}) \
    .join(surgery_df[['event_id', 'procedure_count']].set_index('event_id'),
          on="event_id",
          how="left",
          rsuffix="surgery")

procedure_df = procedure_df.groupby(["procedure", "procedure_count"]).agg({"event_id": "nunique"}).reset_index()
df = procedure_df.pivot(index="procedure", columns="procedure_count", values="event_id").fillna(0)
procedure_counts = df.columns
df = df.reset_index()

procedure_traces = [
    go.Bar(
        x=[procedure_count for procedure_count in procedure_counts],
        y=[df.iloc[i][procedure_count] / sum(df.iloc[i][procedure_counts]) for procedure_count in procedure_counts],
        text=["Count: {0:d}".format(int(df.iloc[i][procedure_count])) for procedure_count in procedure_counts],
        name=df.iloc[i]["procedure"]
    ) for i in range(len(df))
]
procedure_traces_layout = go.Layout(title="Probability of Surgery having n Procedures Conditional on Procedures",
                                    xaxis={'title': 'n-Procedure Surgery'},
                                    yaxis={'title': 'Probability'})

procedure_count_traces = [
    go.Bar(
        x=[df.iloc[i]["procedure"] for i in range(len(df))],
        y=[df.iloc[i][procedure_count] / sum(df[procedure_count]) for i in range(len(df))],
        text=[
            "{1}: {0:d}".format(int(df.iloc[i][procedure_count]),
                                       df.iloc[i]["procedure"])
            for i in range(len(df))
        ],
        hoverinfo='text',
        name="{0:d}-procedure surgery".format(procedure_count)
    ) for procedure_count in procedure_counts
]
procedure_count_traces_layout = go.Layout(
    title="Probability of Performing Procedure Conditional on Surgering Containing n-Procedures",
    xaxis={'title': 'Procedure'},
    yaxis={'title': 'Probability'}
)

procedure_traces_figure = go.Figure(
    data=procedure_traces,
    layout=procedure_traces_layout
)
plot(procedure_traces_figure, filename="{0}_n-procedure_surgery_probability_given_procedure.html".format(case_service))

procedure_count_figure = go.Figure(
    data=procedure_count_traces,
    layout=procedure_count_traces_layout
)
plot(procedure_count_figure, filename="{0}_procedure_probability_given_n-procedure_surgery.html".format(case_service))
