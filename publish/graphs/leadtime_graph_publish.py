import pickle
import plotly
import plotly.graph_objs as go
import matplotlib.pyplot as plt

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
colours = [
    '#08306b', '#08519c', '#2171b5', '#67000d', '#a50f15', '#cb181d'
]
lines = ["-", "--", "-.", "-", "--", "-."]

line_template.layout = dict(font=dict(size=18))
line_template.layout.title = dict(font=dict(size=10))
graph_data = pickle.load(open("publish/graphs/2020-03-06_leadtime_experiment_graph_dat.pickle", "rb"))
"Sin<sup>super</sup>"
data_labels = {
    "backlogging_cost=10_lead_time=0": r'$c_b = 10, L = 0$',
    "backlogging_cost=10_lead_time=1": r'$c_b = 10, L = 1$',
    "backlogging_cost=10_lead_time=2": r'$c_b = 10, L = 2$',
    #"backlogging_cost=10_lead_time=3": "b = 10, L = 3",
    "backlogging_cost=1000_lead_time=0": r'$c_b = 10^3, L = 0$',
    "backlogging_cost=1000_lead_time=1": r'$c_b = 10^3, L = 1$',
    "backlogging_cost=1000_lead_time=2": r'$c_b = 10^3, L = 2$',
    #"backlogging_cost=1000_lead_time=3": "b = 1000, L = 3""
}
traces = []
fig = plt.figure(figsize=(7, 4))
plt.tight_layout()
ax = plt.axes()
ax.set(xlim=(-0.5, 4.5),
       xlabel='Information Horizon', ylabel='Value of ABI (%)',
       title='');
c = 0
for label in data_labels:
    x, y = graph_data["traces"][label]
    y = [100 * d for d in y]
    traces.append(go.Scatter(x=x, y=y, name=data_labels[label]))
    plt.plot(x, y, lines[c], marker='.', color=colours[c], label=data_labels[label])
    c += 1

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

plt.legend()
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
#plt.show()
plt.savefig("lead_time_experiment" + ".svg", format='svg')
plt.savefig("lead_time_experiment" + ".eps", format='eps')
