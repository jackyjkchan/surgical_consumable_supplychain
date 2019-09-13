import dash
import dash_table
import scipy.stats as st
import json

import numpy as np
from scm_analytics.model.SurgeryModel import surgeries_per_day_distribution, pre_process_columns
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import matplotlib.pyplot as plt
import plotly.tools as tls

from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

from dash_app.data_objects import analytics

input_modelling_layout = [
    html.H1("This is the content in tab 2"),
    dcc.Dropdown(
        id="case_service_selection",
        options=[
            {'label': case_service, 'value': case_service}
            for case_service in set(analytics.surgery_df["case_service"])
        ],
        value="Cardiac Surgery"
    ),
    dcc.Input(
        id='binom_sel_n',
        value=1,
        type="number",
        step=1
    ),
    dcc.Input(
        id='binom_sel_p',
        value=1,
        type="number",
        max=1,
        step=0.01
    ),
    dcc.Checklist(
        id='elective_surgery_weekday_demand_use_fit',
        options=[
            {'label': 'Use Best Fit', 'value': 1},
        ],
        value=[],
        labelStyle={'display': 'inline-block'}
    ),
    dcc.Graph(id='weekday_elective_demand_graph')
]

input_modelling_cache = [
    html.Div(id='elective_surgery_demand_empirical_x', style={'display': 'none'}),
    html.Div(id='elective_surgery_demand_empirical_y', style={'display': 'none'}),
    html.Div(id='binom_fit_n', style={'display': 'none'}),
    html.Div(id='binom_fit_p', style={'display': 'none'})
]


def elective_surgery_demand_graph(case_service=None):
    # case_service = "Cardiac Surgery"
    print(case_service)
    surgery_df = pre_process_columns(analytics.surgery_df)
    surgery_df = surgery_df[surgery_df["start_date"].notna()]
    filters = [{"dim": "case_service",
                "op": "eq",
                "val": case_service
                },
               {"dim": "urgent_elective",
                "op": "eq",
                "val": "Elective"
                }]
    dist_df = surgeries_per_day_distribution(surgery_df, day_group_by="is_weekday", filters=filters)

    data = dist_df.set_index("is_weekday").loc[True]["data"]
    empirical = pd.DataFrame()
    empirical["count"] = data
    empirical["frequency"] = True
    empirical = empirical.groupby(["count"]).agg({"frequency": "count"}).reset_index()
    empirical["probability"] = empirical["frequency"] / sum(empirical["frequency"])

    bins = range(1 + int(max(data)))
    binom_x = [x for x in bins]
    n = int(max(data))
    p = np.mean(data) / n

    empirical_trace = go.Bar(
        x=empirical["count"],
        y=empirical["probability"],
        width=0.8,
        opacity=0.75,
        name="Empirical"
    )
    binom_trace = go.Bar(
        x=binom_x,
        y=st.binom.pmf(bins, n, p),
        width=0.2,
        opacity=0.75,
        name="Binomial"
    )
    layout = go.Layout(
        title_text='Elective Surgeries Per Weekday',
        xaxis_title_text='Surgeries Per Day',
        yaxis_title_text='Probability',
        barmode='overlay',
    )
    # fig = go.Figure(data=[empirical_trace,
    #                       binom_trace],
    #                 layout=layout)
    # plot(fig)
    # return {"data": [empirical_trace,
    #                  binom_trace],
    #         "layout": layout}
    empirical_x_json = json.dumps(list(empirical["count"]))
    empirical_y_json = json.dumps(list(empirical["probability"]))
    binom_n_json = json.dumps(n)
    binom_p_json = json.dumps(p)

    return empirical_x_json, empirical_y_json, binom_n_json, binom_p_json
