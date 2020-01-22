import scm_optimization.non_stationary_model as ns_model

import scm_optimization.model as s_model
from scm_optimization.model import DeterministUsageModel, BinomUsageModel, PoissonUsageModel
from scm_implementation.ns_info_state_rvs.ns_info_state_rvs import elective_info_rvs, emergency_info_rvs

import pacal

# case study items, 47320, 56931, 1686, 129636, 83532, 38262
configs = []
item_ids = [id for id in elective_info_rvs]
item_id = "129636"

if __name__ == "__main__":
    ns_configs = []
    i = 0
    for horizon in [0, 1, 2, 3, 4]:
        for b in [100, 1000, 10000]:
            ns_configs.append(ns_model.ModelConfig(
                gamma=1,
                lead_time=0,
                holding_cost=1,
                backlogging_cost=b,
                setup_cost=0,
                unit_price=0,
                usage_model=PoissonUsageModel(scale=1),
                elective_info_state_rv=elective_info_rvs[item_id],
                emergency_info_state_rv=emergency_info_rvs[item_id],
                horizon=horizon,
                label="ns_impl_{}".format(item_id),
                label_index=i))
            i += 1

    xs = list(range(1))
    ts = list(range(7*4))
    ns_model.run_configs(ns_configs, ts, xs)
    #ns_model.run_config((ns_configs[3], ts, xs))
