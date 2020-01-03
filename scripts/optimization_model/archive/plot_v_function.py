from scm_optimization.model import StationaryOptModel
import plotly
import pacal
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot


gamma = 0.9
lead_time = 0
horizon = 2
info_state_rvs = [pacal.ConstDistr(0),
                  pacal.ConstDistr(0),
                  pacal.DiscreteDistr([1, 2, 3, 4], [0.25, 0.25, 0.25, 0.25])]

info_state_rvs = [pacal.DiscreteDistr([1, 2, 3, 4], [0.25, 0.25, 0.25, 0.25]),
                  pacal.ConstDistr(0),
                  pacal.ConstDistr(0)]

holding_cost = 1
backlogging_cost = 10
setup_cost = 5
unit_price = 0

model = StationaryOptModel(gamma,
                           lead_time,
                           horizon,
                           info_state_rvs,
                           holding_cost,
                           backlogging_cost,
                           setup_cost,
                           unit_price)

t = 3
o = (3, 2)
v_values = []
j_values = []
max_inv_pos = 25
y_argmin = model.v_function_argmin(t, o)

for y in range(max_inv_pos):
    v_values.append(model.v_function(t, y, o))

v_function_trace = go.Scatter(
    x=list(range(max_inv_pos)),
    y=v_values,
    name="v_function: (action, info_state) -> expected value"
)

for x in range(max_inv_pos):
    j_values.append(model.j_function(t, x, o))

j_function_trace = go.Scatter(
    x=list(range(max_inv_pos)),
    y=j_values,
    name="j_function: (inv_pos, info_state) -> expected value"
)

layout = go.Layout(title="Expected Cost",
                   xaxis={'title': 'Inventory Position'},
                   yaxis={'title': 'Expected Cost'})

figure = go.Figure(
    data=[v_function_trace,
          j_function_trace],
    layout=layout
)

plot(figure, filename="Expected_Cost_t={0}_o={1}.html".format(str(t), str(o)))