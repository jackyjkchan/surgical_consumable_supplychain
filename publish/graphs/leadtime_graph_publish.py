import pickle
import plotly
import plotly.graph_objs as go

plotly.io.orca.config.executable = 'C:\\Users\\Jacky\\AppData\\Local\\Programs\\orca\\orca.exe'
line_template = go.layout.Template()
line_template.data.scatter = [
    go.Scatter(line=dict(width=2)),
    go.Scatter(line=dict(width=2, dash='dash')),
    go.Scatter(line=dict(width=2, dash='dot')),
    #go.Scatter(line=dict(width=2, dash='dashdot')),
    go.Scatter(line=dict(width=3.5)),
    go.Scatter(line=dict(width=3.5, dash='dash')),
    go.Scatter(line=dict(width=3.5, dash='dot')),
    #go.Scatter(line=dict(width=3.5, dash='dashdot')),
]
line_template.layout = dict(font=dict(size=18))
line_template.layout.title = dict(font=dict(size=10))
graph_data = pickle.load(open("publish/graphs/2020-03-06_leadtime_experiment_graph_dat.pickle", "rb"))

data_labels = {
    "backlogging_cost=10_lead_time=0": "b = 10, L = 0",
    "backlogging_cost=10_lead_time=1": "b = 10, L = 1",
    "backlogging_cost=10_lead_time=2": "b = 10, L = 2",
    #"backlogging_cost=10_lead_time=3": "b = 10, L = 3",
    "backlogging_cost=1000_lead_time=0": "b = 1000, L = 0",
    "backlogging_cost=1000_lead_time=1": "b = 1000, L = 1",
    "backlogging_cost=1000_lead_time=2": "b = 1000, L = 2",
    #"backlogging_cost=1000_lead_time=3": "b = 1000, L = 3""
}
traces = []

for label in data_labels:
    x, y = graph_data["traces"][label]
    traces.append(go.Scatter(x=x, y=y, name=data_labels[label]))

layout = go.Layout(title="",
                   xaxis={'title': 'Information Horizon'},
                   yaxis={'title': 'Value of ABI'},
                   plot_bgcolor="white")
figure = go.Figure(
    data=traces,
    layout=layout
)
figure.update_layout(template=line_template)
figure.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
figure.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
figure.write_image("lead_time_experiment.svg", width=900, height=600)
