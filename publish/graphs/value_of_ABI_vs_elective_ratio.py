import textwrap
import os
import pandas as pd
import pacal
import itertools
from datetime import date

import pickle
import plotly.express as px
import plotly
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

plotly.io.orca.config.executable = 'C:\\Users\\Jacky\\AppData\\Local\\Programs\\orca\\orca.exe'
from scripts.optimization_model.model_configs import action_increment_configs

ratios = [0, 0.2, 0.4, 0.6, 0.8, 1]
value_of_1ABI_Binomial = [0, 0.03143039, 0.06617943, 0.1089374, 0.1717965, 0.2788082]

value_of_1ABI_Poisson = [0, 0.05440618, 0.113353, 0.1827145, 0.2547764, 0.4079284]

traces = []
traces.append(go.Scatter(
    x=ratios,
    y=value_of_1ABI_Binomial,
    name="Binomial Bookings n=10, p=1/2"
))
traces.append(go.Scatter(
    x=ratios,
    y=value_of_1ABI_Poisson,
    name="Binomial Poisson rate=10"
))

layout = go.Layout(title="",
                   xaxis={'title': 'Elective Ratio'},
                   yaxis={'title': 'Value of ABI'},
                   plot_bgcolor="white")
figure = go.Figure(
    data=traces,
    layout=layout
)
plot(figure,
     filename="Value_ABI_vs_Elective_Ratio_{}.html".format(date.today().isoformat()))