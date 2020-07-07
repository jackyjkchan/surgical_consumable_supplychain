import pickle
import plotly
import plotly.graph_objs as go

plotly.io.orca.config.executable = 'C:\\Users\\Jacky\\AppData\\Local\\Programs\\orca\\orca.exe'
line_template = go.layout.Template()
line_template.data.scatter = [
    go.Scatter(marker=dict(color='rgb(8,48,107)'), line=dict(width=2, color='rgb(8,48,107)')),
    go.Scatter(marker=dict(color='rgb(8,81,156)'), line=dict(width=2, dash='dash', color='rgb(8,81,156)')),
    go.Scatter(marker=dict(color='rgb(33,113,181)'), line=dict(width=2, dash='dot', color='rgb(33,113,181)')),
    #go.Scatter(marker=dict(color='rgb(66,145,198)'), line=dict(width=2, dash='dashdot',color='rgb(66,145,198)')),
    go.Scatter(marker=dict(color='rgb(103, 0, 13)'), line=dict(width=2, color='rgb(103, 0, 13)')),
    go.Scatter(marker=dict(color='rgb(165, 15, 21)'), line=dict(width=2, dash='dash', color='rgb(165, 15, 21)')),
    go.Scatter(marker=dict(color='rgb(203, 24, 29)'), line=dict(width=2, dash='dot', color='rgb(203, 24, 29)')),
    #go.Scatter(marker=dict(color='rgb(239,59,44)'), line=dict(width=2, dash='dashdot', color='rgb(239,59,44)')),
]
line_template.layout = dict(font=dict(size=18))
line_template.layout.title = dict(font=dict(size=10))
graph_data = pickle.load(open("publish/graphs/2020-03-06_leadtime_experiment_graph_dat.pickle", "rb"))
"Sin<sup>super</sup>"
data_labels = {
    "backlogging_cost=10_lead_time=0": "C<sub>b</sub> = 10, L = 0",
    "backlogging_cost=10_lead_time=1": "C<sub>b</sub> = 10, L = 1",
    "backlogging_cost=10_lead_time=2": "C<sub>b</sub> = 10, L = 2",
    #"backlogging_cost=10_lead_time=3": "b = 10, L = 3",
    "backlogging_cost=1000_lead_time=0": "C<sub>b</sub> = 10<sup>3</sup>, L = 0",
    "backlogging_cost=1000_lead_time=1": "C<sub>b</sub> = 10<sup>3</sup>, L = 1",
    "backlogging_cost=1000_lead_time=2": "C<sub>b</sub> = 10<sup>3</sup>, L = 2",
    #"backlogging_cost=1000_lead_time=3": "b = 1000, L = 3""
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
                   yaxis=dict(title='Value of ABI (%)',
                              mirror=True, ticks='outside', showline=True,
                              zeroline=False, showgrid=False),
                   plot_bgcolor="white")
figure = go.Figure(
    data=traces,
    layout=layout
)
figure.update_layout(template=line_template)
figure.update_xaxes(showgrid=False, gridwidth=1, gridcolor='lightgrey')
figure.update_yaxes(showgrid=False, gridwidth=1, gridcolor='lightgrey')
figure.write_image("lead_time_experiment.svg", width=600, height=400)
