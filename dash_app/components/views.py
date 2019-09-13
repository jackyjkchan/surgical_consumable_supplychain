import dash
import dash_table

from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

from dash_app.data_objects import analytics

SURGERY_COLS = ["event_id", "scheduled_procedures", "case_service", "start_date", "booking_dt", "urgent_elective"]
USAGE_COLS = ["event_id", "item_id", "code_name", "used_qty", "unit_price"]

usage_table = dash_table.DataTable(
    id='usage_view',
    columns=[{"name": i, "id": i} for i in analytics.usage_df[USAGE_COLS].columns],
    data=analytics.usage_df[0:1000][USAGE_COLS].to_dict('records'),
    style_table={'overflowX': 'scroll'},
    fixed_rows={'headers': True, 'data': 0},
    style_cell={
        # all three widths are needed
        'minWidth': '100px', 'width': '0px', 'maxWidth': '500px',
        'whiteSpace': 'no-wrap',
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
    },
    css=[{
        'selector': '.dash-cell div.dash-cell-value',
        'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
    }],
    filter_action="native",
    sort_action="native",
    sort_mode="multi",
)

surgery_table = dash_table.DataTable(
    id='surgery_view',
    columns=[{"name": i, "id": i} for i in analytics.surgery_df[SURGERY_COLS].columns],
    data=analytics.surgery_df[0:1000][SURGERY_COLS].to_dict('records'),
    style_table={'overflowX': 'scroll'},
    fixed_rows={'headers': True, 'data': 0},
    style_cell={
        # all three widths are needed
        'minWidth': '100px', 'width': '0px', 'maxWidth': '500px',
        'whiteSpace': 'no-wrap',
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
    },
    css=[{
        'selector': '.dash-cell div.dash-cell-value',
        'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
    }],
    filter_action="native",
    sort_action="native",
    sort_mode="multi",
)
