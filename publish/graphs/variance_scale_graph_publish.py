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
graph_data = pickle.load(open("publish/graphs/2020-04-01_variance_scale_graph_dat.pickle", "rb"))

data_labels = {
    "usage_model=Binom 8 0.5_info_rv_str=": "Usage Var=2, Booking Var=0",
    "usage_model=Binom 8 0.5_info_rv_str=Binomial(8.0.5)": "Usage Var=2, Booking Var=2",
    "usage_model=Binom 8 0.5_info_rv_str=Poisson(4.0)": "Usage Var=2, Booking Var=4",
    "usage_model=Const 4_info_rv_str=": "Usage Var=0, Booking Var=0",
    "usage_model=Const 4_info_rv_str=Binomial(8.0.5)": "Usage Var=0, Booking Var=2",
    "usage_model=Const 4_info_rv_str=Poisson(4.0)": "Usage Var=0, Booking Var=4",
    "usage_model=Poisson 4 0.001_info_rv_str=": "Usage Var=4, Booking Var=0",
    "usage_model=Poisson 4 0.001_info_rv_str=Binomial(8.0.5)": "Usage Var=4, Booking Var=2",
    "usage_model=Poisson 4 0.001_info_rv_str=Poisson(4.0)": "Usage Var=4, Booking Var=4",
}
data_labels = {
    #"usage_model=Const 4_info_rv_str=": "Var [0, 0]",
    "usage_model=Const 4_info_rv_str=Binomial(8.0.5)": "Var [0, 2]",
    "usage_model=Const 4_info_rv_str=Poisson(4.0)": "Var [0, 4]",
    "usage_model=Binom 8 0.5_info_rv_str=": "Var [2, 0]",
    "usage_model=Binom 8 0.5_info_rv_str=Binomial(8.0.5)": "Var [2, 2]",
    "usage_model=Binom 8 0.5_info_rv_str=Poisson(4.0)": "Var [2, 4]",
    "usage_model=Poisson 4 0.001_info_rv_str=": "Var [4, 0]",
    "usage_model=Poisson 4 0.001_info_rv_str=Binomial(8.0.5)": "Var [4, 2]",
    "usage_model=Poisson 4 0.001_info_rv_str=Poisson(4.0)": "Var [4, 4]",
}
traces = []

for label in data_labels:
    x, y = graph_data["traces"][label]
    y = [yy*100 for yy in y]
    traces.append(go.Scatter(x=x, y=y, name=data_labels[label]))

layout = go.Layout(title="",
                   xaxis={'title': 'Information Horizon'},
                   yaxis={'title': 'Value of ABI (%)'},
                   plot_bgcolor="white")
figure = go.Figure(
    data=traces,
    layout=layout
)
figure.update_layout(template=line_template)
figure.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
figure.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgrey')
figure.write_image("variance_scale_experiment.svg", width=900, height=600)
