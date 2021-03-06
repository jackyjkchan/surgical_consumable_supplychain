import scm_optimization.non_stationary_model as ns_model

import scm_optimization.model as s_model
from scm_optimization.model import DeterministUsageModel, BinomUsageModel, PoissonUsageModel

import pacal
from decimal import *

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

configs = []


if __name__ == "__main__":
    i = 0
    for horizon in [1, 2, 3, 4]:
        for rv in [rv_4_16, pacal.PoissonDistr(5, trunk_eps=1e-3)]:
            s_rv = [rv_0] * horizon + [rv]
            s_rv = s_rv if horizon else s_rv + [rv_0]
            ns_rv = [s_rv] * 7

            ns_config = ns_model.ModelConfig(
                gamma=0.9,
                lead_time=0,
                holding_cost=1,
                backlogging_cost=10,
                setup_cost=50,
                unit_price=0,
                usage_model=PoissonUsageModel(scale=1),
                ns_info_state_rvs=ns_rv,
                horizon=horizon,
                label="non_stationary_test",
                label_index=i)

            s_config = s_model.ModelConfig(
                gamma=0.9,
                lead_time=0,
                holding_cost=1,
                backlogging_cost=10,
                setup_cost=50,
                unit_price=0,
                usage_model=PoissonUsageModel(scale=1),
                info_state_rvs=s_rv,
                horizon=horizon,
                label="stationary_test",
                label_index=i)
            i += 1

            xs = list(range(0, 1))
            ts = list(range(0, 16))
            ns_model.run_config((ns_config, ts, xs))
            s_model.run_config((s_config, ts, xs))
