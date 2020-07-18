import pickle
import plotly
import plotly.graph_objs as go
import matplotlib.pyplot as plt

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
colours = [
    '#08306b', '#08519c', '#2171b5', '#4291c6', '#6baed6', '#9ecae1'
]
line_template.layout = dict(font=dict(size=18))
line_template.layout.title = dict(font=dict(size=10))
graph_data = pickle.load(open("publish/graphs/2020-07-07_base_experiment_graph_dat.pickle", "rb"))
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

data_labels = {
    "backlogging_cost=10000.0": r'$c_b = 10^4$',
    "backlogging_cost=1000.0": r'$c_b = 10^3$',
    "backlogging_cost=100.0": r'$c_b = 10^2$',
    "backlogging_cost=10.0": r'$c_b = 10^1$',
    "backlogging_cost=1.0": r'$c_b = 10^0$',
    "backlogging_cost=0.001": r'$c_b = 10^{-3}$'
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

    plt.plot(x, y, marker='.', color=colours[c], label=data_labels[label])
    c += 1

layout = go.Layout(title="",
                   xaxis=dict(title='Information Horizon', dtick=1,
                              mirror=True, ticks='outside', showline=True,
                              zeroline=False, showgrid=False),
                   yaxis=dict(title='Value of ABI (%)', dtick=10,
                              mirror=True, ticks='outside', showline=True,
                              zeroline=False, showgrid=False),
                   plot_bgcolor="white",
                   showlegend=True,
                   )
figure = go.Figure(
    data=traces,
    layout=layout
)
figure.update_layout(template=line_template)
figure.update_xaxes(showgrid=False, gridwidth=0.5, gridcolor='lightgrey')
figure.update_yaxes(showgrid=False, gridwidth=1, gridcolor='lightblue')
figure.write_image("basic_experiment.svg", width=900, height=600)

plt.legend()
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
#plt.show()
plt.savefig("basic_experiment" + ".svg", format='svg')
plt.savefig("basic_experiment" + ".eps", format='eps')