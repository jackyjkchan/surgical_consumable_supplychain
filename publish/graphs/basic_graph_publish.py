import pickle
import plotly
import plotly.graph_objs as go
plotly.io.orca.config.executable = 'C:\\Users\\Jacky\\AppData\\Local\\Programs\\orca\\orca.exe'
line_template = go.layout.Template()
line_template.data.scatter = [
    go.Scatter(line=dict(width=2)),
    go.Scatter(line=dict(width=2, dash='dash')),
    go.Scatter(line=dict(width=2, dash='dot')),
    go.Scatter(line=dict(width=2, dash='dashdot')),
    go.Scatter(line=dict(width=3.5)),
    go.Scatter(line=dict(width=3.5, dash='dash')),
    go.Scatter(line=dict(width=3.5, dash='dot')),
    go.Scatter(line=dict(width=3.5, dash='dashdot')),
]
line_template.layout = dict(font=dict(size=18))
line_template.layout.title = dict(font=dict(size=10))
graph_data = pickle.load(open("publish/graphs/2020-02-28_base_experiment_graph_dat.pickle", "rb"))

data_labels = {
    "backlogging_cost=10": "b = 10",
    "backlogging_cost=100": "b = 100",
    "backlogging_cost=1000": "b = 1000",
    "backlogging_cost=10000": "b = 10000"
}
traces = []

for label in data_labels:
    x, y = graph_data["traces"][label]
    traces.append(go.Scatter(x=x, y=y,name=data_labels[label]))

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
figure.write_image("basic_experiment.svg", width=900, height=600)
