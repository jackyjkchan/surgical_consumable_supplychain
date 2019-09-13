import dash
import dash_table
import json

from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

import dash_bootstrap_components as dbc

from dash_app.data_objects import analytics
from dash_app.components.views import surgery_table, usage_table
from dash_app.layouts.demand_modelling import *
from dash_app.layouts.usage_modelling import *

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.GRID])

views = [
    html.Div([html.H3("Surgery Table"),
              html.Div(surgery_table)],
             style={'width': '49%', 'float': 'left'}),
    html.Div([html.H3("Usage Table"),
              html.Div(usage_table)],
             style={'width': '49%', 'float': 'right'})
]

app.layout = html.Div([
    dbc.Row([
        dbc.Col(
            [dcc.Tabs(id="tabs",
                      vertical=True,
                      parent_style={'flex-direction': 'column',
                                    '-webkit-flex-direction': 'column',
                                    '-ms-flex-direction': 'column',
                                    'display': 'flex'},
                      value="0",
                      children=[dcc.Tab(label='Raw Data', value="0"),
                                dcc.Tab(label='Input Modelling', value="1"),
                                dcc.Tab(label='Tab three', value="2")])
             ],
            width=2),
        dbc.Col(
            [html.Div(views, id='tab1'),
             html.Div(input_modelling_layout, id='tab2'),
             html.Div(usage_modelling_layout, id='tab3')],
            width=10)
    ]),
    *input_modelling_cache
])

SURGERY_COLS = ["event_id", "scheduled_procedures", "case_service", "start_date", "booking_dt", "urgent_elective"]
USAGE_COLS = ["event_id", "item_id", "code_name", "used_qty", "unit_price"]


@app.callback([Output('tab1', 'style'),
               Output('tab2', 'style'),
               Output('tab3', 'style')],
              [Input('tabs', 'value')])
def tab_content(tabs_value):
    ret = [{'display': 'none'}] * 3
    ret[int(tabs_value)] = {'display': 'block'}
    print(tabs_value)
    print(ret)
    return ret


# @app.callback(Output('weekday_elective_demand_graph', 'figure'),
#               [Input('case_service_selection', 'value')])
# def call_elective_surgery_demand_graph(case_service_selection):
#     return elective_surgery_demand_graph(case_service_selection)

@app.callback([Output('binom_sel_n', 'min'),
               Output('binom_sel_n', 'max'),
               Output('binom_sel_n', 'value'),
               Output('binom_sel_p', 'min'),
               Output('binom_sel_p', 'max'),
               Output('binom_sel_p', 'value')],
              [Input('elective_surgery_weekday_demand_use_fit', 'value')],
              [State('binom_fit_n', 'children'),
               State('binom_fit_p', 'children')])
def elective_surgery_weekday_demand_use_fit_callback(flag, best_n, best_p):
    print("flag:", flag)
    if flag:
        best_n = json.loads(best_n) if best_n else 1
        best_p = json.loads(best_p) if best_p else 0
        print(best_n, best_p)
        return best_n, best_n, best_n, best_p, best_p, best_p

    else:
        return 0, 100, best_n, 0, 1, best_p


@app.callback([Output('elective_surgery_demand_empirical_x', 'children'),
               Output('elective_surgery_demand_empirical_y', 'children'),
               Output('binom_fit_n', 'children'),
               Output('binom_fit_p', 'children')],
              [Input('case_service_selection', 'value')])
def cache_elective_surgery_demand(case_service_selection):
    return elective_surgery_demand_graph(case_service_selection)


@app.callback(Output('weekday_elective_demand_graph', 'figure'),
              [Input('elective_surgery_demand_empirical_x', 'children'),
               Input('elective_surgery_demand_empirical_y', 'children'),
               Input('binom_fit_n', 'children'),
               Input('binom_fit_p', 'children')])
def update_elective_surgery_demand_graph(empirical_x, empirical_y, best_n, best_p):
    empirical_x = json.loads(empirical_x) if empirical_x else [0]
    empirical_y = json.loads(empirical_y) if empirical_y else [1]
    best_n = json.loads(best_n) if best_n else 1
    best_p = json.loads(best_p) if best_p else 0
    empirical_trace = go.Bar(
        x=empirical_x,
        y=empirical_y,
        width=0.8,
        opacity=0.75,
        name="Empirical"
    )
    binom_trace = go.Bar(
        x=empirical_x,
        y=st.binom.pmf(empirical_x, best_n, best_p),
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
    return {"data": [empirical_trace,
                     binom_trace],
            "layout": layout}


@app.callback(Output('regression_results', 'children'),
              [Input('run_regression', 'n_clicks')],
              [State('item_Selection', 'value'),
               State('case_service_selection', 'value'),
               State('occ_thres', 'value'),
               State('p_thres', 'value')])
def run_regression(click, item_id, case_service, occ_thres, pthres):
    print("run_regression: ", click)
    if click:
        feature_df, r2 = usage_regression_model(case_service, pthres, occ_thres, item_id)
        columns = [{"name": i, "id": i} for i in feature_df.columns]
        data = feature_df.to_dict('records')
        table = dash_table.DataTable(
            id='regression_results_table',
            columns=columns,
            data=data,
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
        print("done")
        print(feature_df)
        return [table]
    return []


if __name__ == '__main__':
    app.run_server(debug=True)
