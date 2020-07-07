import pickle
import plotly
import plotly.graph_objs as go

plotly.io.orca.config.executable = 'C:\\Users\\Jacky\\AppData\\Local\\Programs\\orca\\orca.exe'
line_template = go.layout.Template()
line_template.data.scatter = [
    go.Scatter(marker=dict(color='rgb(8,48,107)'), line=dict(width=2, color='rgb(8,48,107)')),
    go.Scatter(marker=dict(color='rgb(8,81,156)'), line=dict(width=2, color='rgb(8,81,156)')),
    go.Scatter(marker=dict(color='rgb(33,113,181)'), line=dict(width=2, color='rgb(33,113,181)')),
    go.Scatter(marker=dict(color='rgb(66,145,198)'), line=dict(width=2, color='rgb(66,145,198)')),
    go.Scatter(marker=dict(color='rgb(66,145,198)'), line=dict(width=2, color='rgb(107,174,214)')),
    go.Scatter(marker=dict(color='rgb(66,145,198)'), line=dict(width=2, color='rgb(158,202,225)')),
]
line_template.layout = dict(font=dict(size=18))
line_template.layout.title = dict(font=dict(size=10))
graph_data = pickle.load(open("publish/graphs/2020-06-30_base_experiment_graph_dat.pickle", "rb"))
graph_data["traces"]["backlogging_cost=1.0"] = ([0, 1, 2, 3, 4],
                                                [0.0, 0.19589121078347493, 0.1963192048540322, 0.19632587500807264,
                                                 0.19632587500807264])

data_labels = {
    "backlogging_cost=10000.0": "C<sub>b</sub> = 10<sup>4</sub>",
    "backlogging_cost=1000.0": "C<sub>b</sub> = 10<sup>3</sub>",
    "backlogging_cost=100.0": "C<sub>b</sub> = 10<sup>2</sub>",
    "backlogging_cost=10.0": "C<sub>b</sub> = 10",
    "backlogging_cost=1.0": "C<sub>b</sub> = 1",
    "backlogging_cost=0.001": "C<sub>b</sub> = 10<sup>-3</sub>",
}
traces = []

for label in data_labels:
    x, y = graph_data["traces"][label]
    y = [100 * d for d in y]
    traces.append(go.Scatter(x=x, y=y, name=data_labels[label]))

layout = go.Layout(title="",
                   xaxis=dict(title='Information Horizon', dtick=1,
                              mirror=True, ticks='outside', showline=True,
                              zeroline=False, showgrid=False),
                   yaxis=dict(title='Value of ABI (%)', dtick=10,
                              mirror=True, ticks='outside', showline=True,
                              zeroline=False, showgrid=False),
                   plot_bgcolor="white")
figure = go.Figure(
    data=traces,
    layout=layout
)
figure.update_layout(template=line_template)
figure.update_xaxes(showgrid=False, gridwidth=0.5, gridcolor='lightgrey')
figure.update_yaxes(showgrid=False, gridwidth=1, gridcolor='lightblue')
figure.write_image("basic_experiment.svg", width=600, height=400)
