from scm_optimization.model import ModelConfig, run_configs, PoissonUsageModel, BinomUsageModel, DeterministUsageModel, get_model
import pacal
from decimal import *

configs = []
i = 0
usage_models = [
    BinomUsageModel(n=4, p=0.25),
    BinomUsageModel(n=5, p=0.2),
    BinomUsageModel(n=10, p=0.1),
]

policy_usage_model = PoissonUsageModel(1, trunk=1e-10)

booking_models = [
    pacal.BinomialDistr(10, 0.5),
]

for horizon in [0, 1, 2, 3]:
    for b in [1000]:
        for booking_model in booking_models:
            configs.append(ModelConfig(
                gamma=1,
                lead_time=0,
                info_state_rvs=None,
                holding_cost=1,
                backlogging_cost=b,
                setup_cost=0,
                unit_price=0,
                usage_model=policy_usage_model,
                horizon=horizon,
                info_rv=booking_model,
                label="poisson_usage_policy",
                label_index=i)
            )
            i += 1


if __name__ == "__main__":
    xs = list(range(0, 1))
    ts = list(range(0, 21))
    run_configs(configs, ts, xs, pools=4)
