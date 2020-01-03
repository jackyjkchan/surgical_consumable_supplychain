from scm_optimization.model import ModelConfig, run_configs, PoissonUsageModel, BinomUsageModel, DeterministUsageModel
import pacal
from decimal import *

configs = []
i = 0

for demand_n in [1, 2, 3, 4]:
    for usage_n in [1, 2, 3, 4]:
        for p in [0.25, 0.5, 0.75]:
            for q in [0.25, 0.5, 0.75]:
                for horizon in [0, 1, 2, 3, 4, 5]:
                    for b in [0.1, 0.5, 1, 2, 3, 5, 10, 100]:
                        configs.append(ModelConfig(
                            gamma=1,
                            lead_time=0,
                            info_state_rvs=None,
                            holding_cost=1,
                            backlogging_cost=b,
                            setup_cost=0,
                            unit_price=0,
                            usage_model=BinomUsageModel(n=usage_n, p=p),
                            increments=1,
                            horizon=horizon,
                            info_rv=pacal.BinomialDistr(demand_n, q),
                            label="numerical_experiments_binomial_model",
                            label_index=i)
                        )
                        i += 1

if __name__ == "__main__":
    xs = list(range(0, 20))
    ts = list(range(0, 21))
    run_configs(configs, ts, xs, pools=8)
