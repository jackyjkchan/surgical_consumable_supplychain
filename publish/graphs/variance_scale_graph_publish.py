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

line_template.data.scatter = [
    go.Scatter(marker=dict(color='rgb(8,48,107)'), line=dict(width=3, color='rgb(8,48,107)')),
    go.Scatter(marker=dict(color='rgb(8,81,156)'), line=dict(width=3, dash='dash', color='rgb(8,81,156)')),
    go.Scatter(marker=dict(color='rgb(33,113,181)'), line=dict(width=2, dash='dot', color='rgb(33,113,181)')),
    go.Scatter(marker=dict(color='rgb(66,145,198)'), line=dict(width=2, dash='dashdot', color='rgb(66,145,198)')),
    go.Scatter(marker=dict(color='rgb(103, 0, 13)'), line=dict(width=2, color='rgb(103, 0, 13)')),
    go.Scatter(marker=dict(color='rgb(165, 15, 21)'), line=dict(width=2, dash='dash', color='rgb(165, 15, 21)')),
    go.Scatter(marker=dict(color='rgb(203, 24, 29)'), line=dict(width=2, dash='dot', color='rgb(203, 24, 29)')),
    go.Scatter(marker=dict(color='rgb(239,59,44)'), line=dict(width=2, dash='dashdot', color='rgb(239,59,44)')),
]

line_template.layout = dict(font=dict(size=18))
line_template.layout.title = dict(font=dict(size=10))
graph_data = pickle.load(open("publish/graphs/2020-04-01_variance_scale_graph_dat.pickle", "rb"))

data_labels = {
    # "usage_model=Const 4_info_rv_str=": "Var [0, 0]",
    "usage_model=Const 4_info_rv_str=Binomial(8.0.5)": "Var [0, 2]",
    "usage_model=Const 4_info_rv_str=Poisson(4.0)": "Var [0, 4]",
    "usage_model=Binom 8 0.5_info_rv_str=": "Var [2, 0]",
    "usage_model=Binom 8 0.5_info_rv_str=Binomial(8.0.5)": "Var [2, 2]",
    "usage_model=Binom 8 0.5_info_rv_str=Poisson(4.0)": "Var [2, 4]",
    "usage_model=Poisson 4 0.001_info_rv_str=": "Var [4, 0]",
    "usage_model=Poisson 4 0.001_info_rv_str=Binomial(8.0.5)": "Var [4, 2]",
    "usage_model=Poisson 4 0.001_info_rv_str=Poisson(4.0)": "Var [4, 4]",
}

data_labels = {
    "usage_model=Const 4_info_rv_str=Binomial(8.0.5)": "Var<sub>U</sub>=0, Var<sub>B</sub>=2",
    "usage_model=Const 4_info_rv_str=Poisson(4.0)": "Var<sub>U</sub>=0, Var<sub>B</sub>=4",

    "usage_model=Binom 8 0.5_info_rv_str=": "Var<sub>U</sub>=2, Var<sub>B</sub>=0",
    "usage_model=Poisson 4 0.001_info_rv_str=": "Var<sub>U</sub>=4, Var<sub>B</sub>=0",

    "usage_model=Binom 8 0.5_info_rv_str=Poisson(4.0)": "Var<sub>U</sub>=2, Var<sub>B</sub>=4",
    "usage_model=Poisson 4 0.001_info_rv_str=Poisson(4.0)": "Var<sub>U</sub>=4, Var<sub>B</sub>=4",
    "usage_model=Binom 8 0.5_info_rv_str=Binomial(8.0.5)": "Var<sub>U</sub>=2, Var<sub>B</sub>=2",
    "usage_model=Poisson 4 0.001_info_rv_str=Binomial(8.0.5)": "Var<sub>U</sub>=4, Var<sub>B</sub>=2",

}

traces = []

for label in data_labels:
    x, y = graph_data["traces"][label]
    y = [yy * 100 for yy in y]
    traces.append(go.Scatter(x=x, y=y, name=data_labels[label]))

layout = go.Layout(title="",
                   xaxis=dict(title='Information Horizon', dtick=1,
                              mirror=True, ticks='outside', showline=True,
                              zeroline=False, showgrid=False),
                   yaxis=dict(title='Value of ABI (%)',
                              mirror=True, ticks='outside', showline=True,
                              zeroline=False, showgrid=False),
                   plot_bgcolor="white",
                   )
figure = go.Figure(
    data=traces,
    layout=layout
)
figure.update_layout(template=line_template)
figure.update_xaxes(showgrid=False, gridwidth=1, gridcolor='lightgrey')
figure.update_yaxes(showgrid=False, gridwidth=1, gridcolor='lightgrey')
figure.write_image("variance_scale_experiment.svg", width=600, height=400)
