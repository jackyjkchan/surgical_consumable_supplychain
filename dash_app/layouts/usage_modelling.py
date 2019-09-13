from dash_app.data_objects import analytics, usage_regression_model
import dash_table

import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
USAGE_COLS = ["event_id", "item_id", "code_name", "used_qty", "unit_price"]

usage_modelling_layout = [
    html.H1("This is the content in tab 3 for Usage Modelling"),
    dcc.Dropdown(
        id="item_Selection",
        options=[
            {'label': case_service, 'value': case_service}
            for case_service in set(analytics.usage_df["item_id"])
        ],
        value="129636"
    ),
    dcc.Input(
        id='occ_thres',
        placeholder="Min Occurrence (default 5)",
        value=5,
        type="number",
        step=1,
        min=0,
        max=20
    ),
    dcc.Input(
        id='p_thres',
        placeholder="Max P Value (default 0.05)",
        value=0.05,
        type="number",
        min=0,
        max=1,
        step=0.01
    ),
    html.Button(
        "Run Regression",
        id='run_regression'
    ),
    html.Div(children=[],
             id="regression_results")

]
