from scm_optimization.model import StationaryOptModel
import pacal
import itertools
import pandas as pd
import datetime
import time

inv_pos_max = 30
t_max = 0

rv_0 = pacal.ConstDistr(0)
rv_5_5 = pacal.DiscreteDistr([5], [1])
rv_3_7 = pacal.DiscreteDistr([3, 7], [0.5, 0.5])
rv_1_9 = pacal.DiscreteDistr([1, 9], [0.5, 0.5])
rv_0_10 = pacal.DiscreteDistr([0, 10], [0.5, 0.5])

rv_10_10 = pacal.DiscreteDistr([10], [1])
rv_8_12 = pacal.DiscreteDistr([8, 12], [0.5, 0.5])
rv_7_13 = pacal.DiscreteDistr([7, 13], [0.5, 0.5])
rv_6_14 = pacal.DiscreteDistr([6, 14], [0.5, 0.5])
rv_5_15 = pacal.DiscreteDistr([5, 15], [0.5, 0.5])
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

info_horizons = [1]
usage_models = {
    "Poisson": (lambda o: pacal.PoissonDistr(o, trunk_eps=1e-3), 1)
}
demand_models = {
    "E[Demand] 6, 14": rv_6_14,
}

fn = "batch_mdp_results_non_convex_cases_action_inc_v2_20191003_01.pickle"

setup_cost = 50
gamma = 0.9
lead_time = 0
holding_cost = 1
backlogging_cost = 10
unit_price = 0
action_inc = 0.1

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
                                'order_up_to',
                                'action_inc'])

print(datetime.datetime.now().isoformat())


usage_model, p = usage_models["Poisson"]

model = StationaryOptModel(gamma,
                           lead_time,
                           [rv_0, rv_6_14],
                           holding_cost,
                           backlogging_cost,
                           setup_cost,
                           unit_price,
                           usage_model=usage_model,
                           increments=action_inc)


print(datetime.datetime.now().isoformat())
