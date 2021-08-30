import pickle
import plotly
import pandas as pd
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
    '#08306b', '#2171b5', '#9ecae1'
]

data_labels = {
    1000: r'$c_b = 10^3$',
    100: r'$c_b = 10^2$',
    10: r'$c_b = 10^1$',
}

line_template.layout = dict(font=dict(size=18))
line_template.layout.title = dict(font=dict(size=10))
la_data = pd.read_csv("publish/graphs/ALL_LA_MDP_RESULTS - Export.csv")
db_data = pd.read_csv("publish/graphs/ALL_DB_MDP_RESULTS - Export.csv")

fig = plt.figure(figsize=(6, 3.5))
ax = plt.axes()
ax.set(xlim=(-0.5, 3.5),
       xlabel='Information Horizon', ylabel='Optimality Gap (%)',
       title='')

c = 0
for backlogging_cost in [1000, 100, 10]:
    x_la = la_data[la_data['backlogging_cost'] == backlogging_cost]["info"]
    y_la = la_data[la_data['backlogging_cost'] == backlogging_cost]["optimality_gap"] * 100
    error_la = la_data[la_data['backlogging_cost'] == backlogging_cost]["gap_ci"] * 100
    plt.errorbar(x_la, y_la, error_la,
                 marker='.',
                 color=colours[c],
                 label="LA Policy, {}".format(data_labels[backlogging_cost])
                 )
    c += 1

c = 0
for backlogging_cost in [1000, 100, 10]:
    x_db = db_data[db_data['backlogging_cost'] == backlogging_cost]["info"]
    y_db = db_data[db_data['backlogging_cost'] == backlogging_cost]["optimality_gap"] * 100
    error_db = db_data[db_data['backlogging_cost'] == backlogging_cost]["gap_ci"] * 100
    plt.errorbar(x_db, y_db, error_db,
                 marker='.',
                 ls='--',
                 color=colours[c],
                 label="DB Policy, {}".format(data_labels[backlogging_cost])
                 )
    c += 1

plt.legend()
plt.tight_layout()
box = ax.get_position()
import matplotlib.ticker as plticker

loc = plticker.MultipleLocator(base=10)  # this locator puts ticks at regular intervals
ax.yaxis.set_major_locator(loc)
ax.set_position([box.x0, box.y0, box.width * 0.65, box.height])
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
#plt.show()

plt.savefig("heuristic_optimality_gap" + ".svg", format='svg')
plt.savefig("heuristic_optimality_gap" + ".eps", format='eps')