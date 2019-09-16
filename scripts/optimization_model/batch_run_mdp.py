from scm_optimization.model import StationaryOptModel
import plotly
import pacal
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import itertools
import pandas as pd
import datetime
import time

inv_pos_max = 30
t_max = 15

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
rv_8_16 = pacal.DiscreteDistr([8, 16], [0.5, 0.5])


test_cases_set_all = {
    "E[Demand] 10": rv_10_10,
    "E[Demand] 8, 12": rv_8_12,
    "E[Demand] 6, 14": rv_6_14,
    "E[Demand] 4, 16": rv_4_16,
    "E[Demand] 2, 18": rv_2_18,
    "E[Demand] 0, 20": rv_0_20
}

test_cases_set1 = {
    "E[Demand] 8, 16": rv_8_16
}


# usage_models = {
#     "Poisson": (lambda o: pacal.PoissonDistr(o, trunk_eps=1e-3), 1),
#     "Deterministic": (lambda o: pacal.ConstDistr(o), 1)
# }
info_horizons = [0, 2, 3]
info_horizons = [3]
usage_models = {
    #"Poisson": (lambda o: pacal.PoissonDistr(o, trunk_eps=1e-3), 1)
    "Binomial p=8/32": (lambda o: pacal.BinomialDistr(int(o), p=0.25), 0.25),
    # "Binomial p=8/16": (lambda o: pacal.BinomialDistr(int(o), p=0.5), 0.5),
    # "Binomial p=8/13": (lambda o: pacal.BinomialDistr(int(o), p=8/13), 8/13),
    # "Binomial p=8/11": (lambda o: pacal.BinomialDistr(int(o), p=8/11), 8/11),
    # "Binomial p=8/10": (lambda o: pacal.BinomialDistr(int(o), p=8/10), 8/10),
    # "Binomial p=8/9": (lambda o: pacal.BinomialDistr(int(o), p=8/9), 8/9),
    # "Deterministic": (lambda o: pacal.ConstDistr(o), 1)
}
demand_models = {
    # "Poisson": pacal.PoissonDistr(8, trunk_eps=1e-3),
    "Binomial p=8/32": pacal.BinomialDistr(32, p=0.25),
    # "Binomial p=8/16": pacal.BinomialDistr(16, p=0.5),
    # "Binomial p=8/13": pacal.BinomialDistr(13, p=8/13),
    # "Binomial p=8/11": pacal.BinomialDistr(11, p=8/11),
    # "Binomial p=8/10": pacal.BinomialDistr(10, p=8/10),
    # "Binomial p=8/9": pacal.BinomialDistr(9, p=8/9),
    # "Deterministic": pacal.ConstDistr(8)
}

test_cases = test_cases_set1
fn = "batch_mdp_results_demand_x_usage_variance_20190916_01.pickle"

setup_costs = [0, 5, 20, 50]
setup_costs = [20]
gamma = 0.9
lead_time = 0
holding_cost = 1
backlogging_cost = 10
unit_price = 0

results = pd.DataFrame(columns=['exogenous_label',
                                'usage_model',
                                'info_rv',
                                'gamma',
                                'holding_cost',
                                'backlogging_cost',
                                'setup_cost',
                                'unit_price',
                                'information_horizon',
                                'lead_time',
                                't',
                                'inventory_position_state',
                                'information_state',
                                'j_value_function',
                                'base_stock',
                                'order_up_to'])

print(datetime.datetime.now().isoformat())

for usage_model_label in usage_models:
    print(usage_model_label)
    usage_model, p = usage_models[usage_model_label]
    scale = 1.0 / p
    for case in demand_models:
        print("\t", case)
        info_rv = demand_models[case] * scale
        print("\t", info_rv.get_piecewise_pdf().getDiracs())
        info_vals = [diracs.a for diracs in info_rv.get_piecewise_pdf().getDiracs()]
        for setup_cost in setup_costs:
            print("\t\tk=", setup_cost)
            for n in info_horizons:
                print("\t\t\tn=", n)
                print(datetime.datetime.now().isoformat())
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
                                           unit_price,
                                           usage_model=usage_model)

                for t in range(t_max + 1):
                    print("\t\t\t\tt=", t)
                    for o in info_states:
                        for x in range(inv_pos_max + 1):
                            j_value = model.j_function(t, x, o)
                            base_stock = model.base_stock_level(t, o)
                            stock_up = model.stock_up_level(t, o)
                            result = {'exogenous_label': case,
                                      'usage_model': usage_model_label,
                                      'info_rv': info_rv,
                                      'gamma': gamma,
                                      'holding_cost': holding_cost,
                                      'backlogging_cost': backlogging_cost,
                                      'setup_cost': setup_cost,
                                      'unit_price': unit_price,
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

                        # results.to_csv("optimization_model_results.csv")
            results.to_pickle(fn)

print(datetime.datetime.now().isoformat())
