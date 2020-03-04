from scm_optimization.model import ModelConfig, run_configs, PoissonUsageModel, BinomUsageModel, DeterministUsageModel
import pacal
from decimal import *

configs = []
i = 0


for horizon in [0, 1, 2, 3, 4]:
    for b in [10, 1000]:
        for k in [1, 10, 50, 100]:
            configs.append(ModelConfig(
                gamma=1,
                lead_time=0,
                info_state_rvs=None,
                holding_cost=1,
                backlogging_cost=b,
                setup_cost=k,
                unit_price=0,
                usage_model=PoissonUsageModel(1),
                horizon=horizon,
                info_rv=pacal.BinomialDistr(10, 0.5),
                label="setup_cost_experiment",
                label_index=i)
            )
            i += 1

if __name__ == "__main__":
    xs = list(range(0, 1))
    ts = list(range(0, 21))
    run_configs(configs, ts, xs, pools=8)
