from scm_optimization.model import ModelConfig, run_configs, PoissonUsageModel, BinomUsageModel, DeterministUsageModel
import pacal
from decimal import *


rv_0 = pacal.ConstDistr(0)
rv_0_1 = pacal.DiscreteDistr([0, 1], [0.5, 0.5])
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

rvs = [rv_4_16, rv_2_18, rv_0_20]
rvs = [rv_0_1]

configs = []
i = 0

usage_models = list(BinomUsageModel(n=1, p=p) for p in [0.6])

for rv in rvs:
    for horizon in [0, 1, 2, 3, 4, 5, 6]:
        for u in usage_models:
            for b in [100]:
                for h in [100]:
                    configs.append(ModelConfig(
                        gamma=1,
                        lead_time=0,
                        info_state_rvs=None,
                        holding_cost=h,
                        backlogging_cost=b,
                        setup_cost=0,
                        unit_price=0,
                        usage_model=u,
                        increments=1,
                        horizon=horizon,
                        info_rv=rv,
                        label="base_case_non_convex_bh_100",
                        label_index=i)
                    )
                    i += 1

if __name__ == "__main__":
    xs = list(range(0, 3))
    ts = list(range(0, 20))
    run_configs(configs, ts, xs, pools=8)
