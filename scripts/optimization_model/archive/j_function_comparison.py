from scm_optimization.model import StationaryOptModel
import plotly
import pacal
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import itertools
import pandas as pd

inv_pos_max = 30
t_max = 15
n_max = 5

rv_0 = pacal.ConstDistr(0)
rv_5_5 = pacal.DiscreteDistr([5], [1])
rv_3_7 = pacal.DiscreteDistr([3, 7], [0.5, 0.5])
rv_1_9 = pacal.DiscreteDistr([1, 9], [0.5, 0.5])
rv_0_10 = pacal.DiscreteDistr([0, 10], [0.5, 0.5])

rv_10_10 = pacal.DiscreteDistr([10], [1])
rv_8_12 = pacal.DiscreteDistr([8, 12], [0.5, 0.5])
rv_6_14 = pacal.DiscreteDistr([6, 14], [0.5, 0.5])
rv_4_16 = pacal.DiscreteDistr([4, 16], [0.5, 0.5])
rv_2_18 = pacal.DiscreteDistr([2, 18], [0.5, 0.5])
rv_0_20 = pacal.DiscreteDistr([0, 20], [0.5, 0.5])

test_cases = {
    "E[Demand] 10": rv_10_10,
    "E[Demand] 8, 12": rv_8_12,
    "E[Demand] 6, 14": rv_6_14,
    "E[Demand] 4, 16": rv_4_16,
    "E[Demand] 2, 18": rv_2_18,
    "E[Demand] 0, 20": rv_0_20
}

gamma = 0.9
lead_time = 0
holding_cost = 1
backlogging_cost = 10
setup_cost = 5
unit_price = 0

results = pd.DataFrame(columns=['exogenous_label',
                                'information_horizon',
                                'lead_time',
                                't',
                                'inventory_position_state',
                                'information_state',
                                'j_value_function',
                                'base_stock',
                                'order_up_to'])
for case in test_cases:
    info_rv = test_cases[case]
    info_vals = [diracs.a for diracs in info_rv.get_piecewise_pdf().getDiracs()]
    for n in range(n_max + 1):
        print(case, n)
        if n == 0:
            info_rv_vector = [info_rv, rv_0]
            horizon = 1
            info_states = [(0,)]
        else:
            info_rv_vector = [rv_0] * n + [info_rv]
            horizon = n
            info_states = [tuple(state) for state in itertools.product(info_vals, repeat=n)]

        model = StationaryOptModel(gamma,
                                   lead_time,
                                   horizon,
                                   info_rv_vector,
                                   holding_cost,
                                   backlogging_cost,
                                   setup_cost,
                                   unit_price)

        for t in range(t_max + 1):
            for o in info_states:
                for x in range(inv_pos_max + 1):
                    j_value = model.j_function(t, x, o)
                    base_stock = model.base_stock_level(t, o)
                    stock_up = model.stock_up_level(t, o)

                    result = {'exogenous_label': case,
                              'information_horizon': n,
                              'lead_time': 0,
                              't': t,
                              'inventory_position_state': x,
                              'information_state': o,
                              'j_value_function': j_value,
                              'base_stock': base_stock,
                              'order_up_to': stock_up
                              }
                    results = results.append(result, ignore_index=True)

results.to_csv("optimization_model_results.csv")
results.to_pickle("batch_mdp_results_20190824.pickle")

#     print(x)
#     j_values.append(model.j_function(t, x, o))
#
# traces[case] = go.Scatter(
#     x=list(range(max_inv_pos)),
#     y=j_values,
#     name=case
# )
#
# layout = go.Layout(title="Value Function J",
#                    xaxis={'title': 'Inventory Position'},
#                    yaxis={'title': 'Optimal Expected Cost'})
#
# figure = go.Figure(
#     data=[traces[case] for case in traces],
#     layout=layout
# )
#
# plot(figure, filename="Expected_Cost_Comparison_T={0}.html".format(str(t)))
