from scm_optimization.model import StationaryOptModel, ModelConfig, run_configs, run_config
from scripts.optimization_model.model_configs import action_increment_configs, \
    non_convex_search_deterministic_usage_configs, leadtime_configs

if __name__ == "__main__":
    xs = [0]
    ts = list(range(0, 25))
    print(action_increment_configs.configs)
    run_configs(non_convex_search_deterministic_usage_configs.configs, ts, xs, pools=8)
    run_configs(leadtime_configs.configs, ts, xs, pools=8)
