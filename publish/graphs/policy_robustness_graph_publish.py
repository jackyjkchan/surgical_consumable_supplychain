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
blues = ['#08306b', '#08519c', '#2171b5', '#4291c6', '#6baed6']
reds = ['#67000d', '#a50f15', '#cb181d', '#ef3b2c', '#fb6a4a']
colours = blues[0:4] + reds[0:4]
lines = ["-", "--", "-.", ":", "-", "--", "-.", ":"]

line_template.layout = dict(font=dict(size=18))
line_template.layout.title = dict(font=dict(size=10))
graph_data = pickle.load(
    open("publish/graphs/2020-07-07_poisson_policy_binomial_usage_robustness_graph_dat.pickle", "rb"))

data_labels = {
    'label=binomial_usage_model_usage_model=Binom 2 0.5': r'$Optimal - Disp. = 0.50$',
    'label=binomial_usage_model_usage_model=Binom 3 0.3333': r'$Optimal - Disp. = 0.67$',
    'label=binomial_usage_model_usage_model=Binom 4 0.25': r'$Optimal - Disp. = 0.75$',
    'label=binomial_usage_model_usage_model=Binom 5 0.2': r'$Optimal - Disp. = 0.80$',
    'label=binomial_usage_model_usage_model=Binom 10 0.1': r'$Optimal - Disp. = 0.90$',

    'label=poisson_policy_binomial_usage_usage_model=Binom 2 0.5': r'$Poisson - Disp. = 0.5$',
    'label=poisson_policy_binomial_usage_usage_model=Binom 3 0.3333': r'$Poisson - Disp. = 0.67$',
    'label=poisson_policy_binomial_usage_usage_model=Binom 4 0.25': r'$Poisson - Disp. = 0.75$',
    'label=poisson_policy_binomial_usage_usage_model=Binom 5 0.2': r'$Poisson - Disp. = 0.80$',
    'label=poisson_policy_binomial_usage_usage_model=Binom 10 0.1': r'$Poisson - Disp. = 0.90$'
}

data_labels = {
    'label=poisson_policy_binomial_usage_usage_model=Binom 10 0.1': r'$\pi^{\mathcal{P}}, CV = 0.90$',
    'label=poisson_policy_binomial_usage_usage_model=Binom 5 0.2': r'$\pi^{\mathcal{P}}, CV = 0.80$',
    'label=poisson_policy_binomial_usage_usage_model=Binom 4 0.25': r'$\pi^{\mathcal{P}}, CV = 0.75$',
    'label=poisson_policy_binomial_usage_usage_model=Binom 3 0.3333': r'$\pi^{\mathcal{P}}, CV = 0.67$',
    'label=binomial_usage_model_usage_model=Binom 10 0.1': r'$\pi^{*}, CV = 0.90$',
    'label=binomial_usage_model_usage_model=Binom 5 0.2': r'$\pi^{*}, CV = 0.80$',
    'label=binomial_usage_model_usage_model=Binom 4 0.25': r'$\pi^{*}, CV = 0.75$',
    'label=binomial_usage_model_usage_model=Binom 3 0.3333': r'$\pi^{*}, CV = 0.67$'
}
traces = []

fig = plt.figure(figsize=(6, 3.5))
# plt.tight_layout()
ax = plt.axes()
ax.set(xlim=(-0.5, 3.5),
       xlabel='Information Horizon', ylabel='Cost to go',
       title='');
plt.xticks([0, 1, 2, 3])

c = 0
for label in data_labels:
    x, y = graph_data["traces"][label]
    y = [d for d in y]
    traces.append(go.Scatter(x=x, y=y, name=data_labels[label]))

    plt.plot(x, y, lines[c], marker='.', color=colours[c], label=data_labels[label])
    c += 1

layout = go.Layout(title=None,
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

plt.legend()
plt.tight_layout()
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.65, box.height])
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
# plt.show()
plt.savefig("policy_robustness_experiment" + ".svg", format='svg')
plt.savefig("policy_robustness_experiment" + ".eps", format='eps')

ppfix = "label=poisson_policy_binomial_usage_usage_model="
bpfix = "label=binomial_usage_model_usage_model="
labels = [
    '{}Binom 3 0.3333',
    '{}Binom 4 0.25',
    '{}Binom 5 0.2',
    '{}Binom 10 0.1']
relative_optimality_gap = {"cv": [0.67, 0.75, 0.8, 0.9],
                           "gap": [
                               graph_data["traces"][label.format(ppfix)][1][1] /
                               graph_data["traces"][label.format(bpfix)][1][0]
                               - graph_data["traces"][label.format(bpfix)][1][1] /
                               graph_data["traces"][label.format(bpfix)][1][0]
                               for label in labels]
                           }

fig = plt.figure(figsize=(6, 3.5))
ax = plt.axes()
ax.set(xlim=(0.65, 0.91),
       xlabel='Information Horizon', ylabel='Optimality Gap (%)',
       title='');
plt.xticks(relative_optimality_gap["cv"])
plt.plot(relative_optimality_gap["cv"],
         [100*x for x in relative_optimality_gap["gap"]],
         lines[0],
         marker='.',
         color=colours[0])
