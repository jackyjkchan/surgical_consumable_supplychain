from scm_optimization.model import ModelConfig, run_configs, PoissonUsageModel, BinomUsageModel, DeterministUsageModel
import pacal
from decimal import *

configs = []
i = 0


for horizon in [0, 1, 2, 3, 4]:
    for b in [10, 1000]:
        for d in [1, 5, 10, 20]:
            configs.append(ModelConfig(
                gamma=1,
                lead_time=0,
                info_state_rvs=None,
                holding_cost=1,
                backlogging_cost=b,
                setup_cost=0,
                unit_price=0,
                usage_model=PoissonUsageModel(1),
                horizon=horizon,
                info_rv=pacal.BinomialDistr(d, 0.5),
                label="demand_scale_experiment",
                label_index=i)
            )
            i += 1
configs = [configs[35], configs[39]]
if __name__ == "__main__":
    xs = list(range(0, 1))
    ts = list(range(0, 21))
    run_configs(configs, ts, xs, pools=8)
