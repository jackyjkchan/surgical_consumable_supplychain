from scm_optimization.model import ModelConfig, run_configs, PoissonUsageModel, BinomUsageModel, DeterministUsageModel, \
    get_model, StationaryOptModel
import pacal
import pickle
import os
from datetime import date, datetime
import time
import pandas as pd
from decimal import *
from multiprocessing import Pool
import math
import os
import pacal
import itertools
import numpy
import time
import pandas as pd
import pickle

from multiprocessing import Pool
from datetime import date, datetime

configs = []
i = 0
binomial_usage_models = [
    BinomUsageModel(n=2, p=0.5),
    BinomUsageModel(n=3, p=0.3333),
    BinomUsageModel(n=4, p=0.25),
    BinomUsageModel(n=5, p=0.2),
    BinomUsageModel(n=10, p=0.1),
]
b = 1000
poisson_usage_model = PoissonUsageModel(1, trunk=1e-10)

booking_model = pacal.BinomialDistr(10, 0.5)

for horizon in [0, 1, 2, 3]:
    configs.append(ModelConfig(
        gamma=1,
        lead_time=0,
        info_state_rvs=None,
        holding_cost=1,
        backlogging_cost=b,
        setup_cost=0,
        unit_price=0,
        usage_model=poisson_usage_model,
        horizon=horizon,
        info_rv=booking_model,
        label="poisson_usage_policy",
        label_index=i)
    )
    i += 1

binomial_usage_configs = []
i = 0
for horizon in [0, 1, 2, 3]:
    for usage_model in binomial_usage_models:
        binomial_usage_configs.append(ModelConfig(
            gamma=1,
            lead_time=0,
            info_state_rvs=None,
            holding_cost=1,
            backlogging_cost=b,
            setup_cost=0,
            unit_price=0,
            usage_model=usage_model,
            horizon=horizon,
            info_rv=booking_model,
            label="binomial_usage_model",
            label_index=i)
        )
        i += 1


def run_robustness_config(args):
    robustness_config, ts, xs = args
    config, argmin, base_stock = robustness_config
    results = pd.DataFrame(columns=['label',
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
                                    'information_state_p',
                                    'j_value_function',
                                    'base_stock',
                                    'order_up_to',
                                    'increments'])
    model = StationaryOptModel(config.params["gamma"],
                               config.params["lead_time"],
                               config.params["info_state_rvs"],
                               config.params["holding_cost"],
                               config.params["backlogging_cost"],
                               config.params["setup_cost"],
                               config.params["unit_price"],
                               increments=config.params["increments"],
                               usage_model=config.params["usage_model"],
                               detailed=config.params["detailed"])

    poisson_model = pickle.load(open(
        "2020-07-07_poisson_usage_policy/2020-07-07_poisson_usage_policy_{}_model.pickle".format(str(horizon)),
        "rb")
    )
    model.value_function_v_argmin = argmin
    model.base_stock_level_cache = base_stock

    print("Starting {}: {}".format(config.sub_label, datetime.now().isoformat()))
    s = time.time()
    for t in ts:
        for x in xs:
            for o in model.info_states():
                info_p = model.get_info_state_prob(o)
                j_value = model.j_function(t, x, o)

                base_stock = model.base_stock_level(t, o)
                stock_up = model.stock_up_level(t, o)

                result = dict(config.params)
                result.update({'label': config.label,
                               't': t,
                               'inventory_position_state': x,
                               'information_state': o,
                               'information_state_p': info_p,
                               'j_value_function': j_value,
                               'base_stock': base_stock,
                               'order_up_to': stock_up})
                results = results.append(result, ignore_index=True)
        results.to_pickle(config.results_fn)
    duration = time.time() - s
    print("Finished {}: {} - {}".format(config.sub_label, datetime.now().isoformat(), str(duration)))
    if not os.path.exists("{}_{}".format(date.today().isoformat(), config.label)):
        os.mkdir("{}_{}".format(date.today().isoformat(), config.label))
    model.to_pickle("{}_{}/{}".format(date.today().isoformat(), config.label, config.sub_label))


def run_robustness_configs(robustness_configs, ts, xs, pools=8):
    print("Starting {} Runs: {}".format(str(len(robustness_configs)), datetime.now().isoformat()))
    #Pool(pools).map(run_robustness_config, list((config, ts, xs) for config in configs))
    results = list(pd.read_pickle(config.results_fn) for config, _, _ in robustness_configs)
    results = pd.concat(results)
    merged_fn = "{}_{}.pickle".format(date.today().isoformat(), robustness_configs[0].label)
    results.to_pickle(merged_fn)
    for config in robustness_configs:
        os.remove(config.results_fn)


if __name__ == "__main__":
    xs = list(range(0, 1))
    ts = list(range(0, 21))
    #run_configs(configs, ts, xs, pools=4)

    #run_configs(binomial_usage_configs, ts, xs, pools=8)

    poisson_policy_binomial_usage_configs = []
    i = 0
    for horizon in [0, 1, 2, 3]:
        # for horizon in [0, 1]:
        poisson_model = pickle.load(open(
            "2020-07-07_poisson_usage_policy/2020-07-07_poisson_usage_policy_{}_model.pickle".format(str(horizon)),
            "rb")
        )
        value_function_v_argmin = poisson_model.value_function_v_argmin
        base_stock_level_cache = poisson_model.base_stock_level_cache
        for usage_model in binomial_usage_models:
            config = ModelConfig(
                gamma=1,
                lead_time=0,
                info_state_rvs=None,
                holding_cost=1,
                backlogging_cost=b,
                setup_cost=0,
                unit_price=0,
                usage_model=usage_model,
                horizon=horizon,
                info_rv=booking_model,
                label="poisson_policy_binomial_usage",
                label_index=i)
            i += 1
            poisson_policy_binomial_usage_configs.append((config, value_function_v_argmin, base_stock_level_cache))
    run_robustness_configs(poisson_policy_binomial_usage_configs, ts, xs)
