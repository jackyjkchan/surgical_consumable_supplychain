import pandas as pd
import os
from itertools import combinations
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from dash_app.data_objects import analytics, usage_regression_model

from scm_analytics import ScmAnalytics
from scm_analytics.config import lhs_config
from scm_analytics.model.SurgeryUsageRegressionModel import Interaction
from scm_analytics.model import SurgeryUsageRegressionModel as SURegressionModel



usage_modelling_layout = [
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