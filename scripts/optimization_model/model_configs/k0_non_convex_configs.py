from scm_optimization.model import ModelConfig, run_configs, PoissonUsageModel, BinomUsageModel, DeterministUsageModel
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


rv_0_1 = pacal.DiscreteDistr([0, 1], [0.5, 0.5])
rv_0_2 = pacal.DiscreteDistr([0, 2], [0.5, 0.5])
rv_0_3 = pacal.DiscreteDistr([0, 3], [0.5, 0.5])


def geometric_rv(p):
    trunk = 1e-3
    limit = 0
    while (1-p)**(limit+1) > trunk:
        limit += 1
    limit += 1
    values = list(range(limit))
    probs = list(p*(1-p)**k for k in values)
    scale = 1 / sum(probs)
    probs = list(p * scale for p in probs)
    return pacal.DiscreteDistr(values, probs)


rv_geometric_80 = geometric_rv(0.8)
rv_geometric_70 = geometric_rv(0.7)
rv_geometric_65 = geometric_rv(0.6)

rvs = [rv_geometric_70]
configs = []
i = 0

usage_models = [PoissonUsageModel(scale=1)]

for rv in rvs:
    for horizon in [0, 1, 2, 3, 4]:
        for u in usage_models:
            for b in [0.001, 1, 10, 100, 1000, 10000]:
                for h in [1]:
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
                        label="k0_geometric_bookings",
                        label_index=i)
                    )
                    i += 1

if __name__ == "__main__":
    xs = list(range(0, 30))
    ts = list(range(0, 21))
    run_configs(configs, ts, xs, pools=8)
