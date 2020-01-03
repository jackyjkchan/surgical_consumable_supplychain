from scm_optimization.model import ModelConfig, run_configs, BinomUsageModel, DeterministUsageModel, get_model
import pacal
from numpy import mean
from decimal import *
import copy

rv_0_1 = pacal.DiscreteDistr([0, 1], [0.5, 0.5])
rvs = [rv_0_1]

configs = []
i = 0

h = 50
b = 50
usage_n = 1
usage_p = 0.6
info_n = 1
info_p = 0.5

params = {"h": 50,
          "b": 50,
          "usage_n": 3,
          "usage_p": 0.6}


def get_neighbours(params):
    int_params = {"h", "b", "usage_n"}
    prob_params = {"usage_p"}
    neighbours = []
    for param in params:
        neighbour = copy.copy(params)
        if param in int_params:
            neighbour[param] = min(100, neighbour[param]+1)
        else:
            neighbour[param] = min(1, neighbour[param] + 0.01)
        if neighbour != params:
            neighbours.append(neighbour)

        neighbour = copy.copy(params)
        if param in int_params:
            neighbour[param] = max(1, neighbour[param] - 1)
        else:
            neighbour[param] = max(0.01, neighbour[param] - 0.01)
        if neighbour != params:
            neighbours.append(neighbour)
    return neighbours


def non_convexity(params):
    t = 1
    x = 0
    confs = list(ModelConfig(
        gamma=1,
        lead_time=0,
        info_state_rvs=None,
        holding_cost=params["h"],
        backlogging_cost=params["b"],
        setup_cost=0,
        unit_price=0,
        usage_model=BinomUsageModel(n=params["usage_n"], p=params["usage_p"]),
        increments=1,
        horizon=n,
        info_rv=rv_0_1,
        label="base_case_non_convex_bh_100",
        label_index=i
    ) for n in [0, 1, 2])

    model_0 = get_model(confs[0])
    model_1 = get_model(confs[1])
    model_2 = get_model(confs[2])

    j0 = mean([model_0.j_function(t, x, info_state) for info_state in model_0.info_states()])
    j1 = mean([model_1.j_function(t, x, info_state) for info_state in model_1.info_states()])
    j2 = mean([model_2.j_function(t, x, info_state) for info_state in model_2.info_states()])
    metric = 1 if j0 == j1 and j1 == j2 else (j1 - j2) / (j0 - j1)
    return metric


best_metric = non_convexity(params)
next_params = params
params = None
count = 0

while next_params != params:
    params = next_params
    neighbours = get_neighbours(params)
    print(len(neighbours))
    for neighbour in neighbours:
        metric = non_convexity(neighbour)
        print(metric)
        if metric > best_metric:
            best_metric = metric
            next_params = neighbour
    count += 1
    if count % 10 == 0:
        print("iterations: ", count)
        print(next_params)
        print("metric: ", best_metric )

print("iterations: ", count)
print(next_params)
print("metric: ", best_metric )
