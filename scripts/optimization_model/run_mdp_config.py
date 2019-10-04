from scm_optimization.model import StationaryOptModel, ModelConfig, run_configs, run_config
from scripts.optimization_model.model_configs import action_increment_configs

if __name__ == "__main__":
    xs = [0]
    ts = list(range(0, 16))
    print(action_increment_configs.configs)
    run_configs(action_increment_configs.configs, ts, xs, pools=4)
