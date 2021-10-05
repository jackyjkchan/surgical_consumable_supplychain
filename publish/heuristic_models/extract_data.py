import pandas as pd
from scm_optimization.heuristic_models import LA_DB_Model

df = pd.DataFrame()
for b in [10, 100, 1000]:
    for info in [0,1,2,3]:
        model = LA_DB_Model.read_pickle(
            "publish/heuristic_models/la_base_experiments/LA_Model_b_{}_info_{}_t_20_model.pickle".format(b, info)
        )
        cost = 0
        for o in model.info_states_prob_cache:
            cost += model.info_states_prob_cache[o] * model.value_function_j[(20, 0, o)]


        df = df.append(
            {
                "b": b,
                "info": info,
                "cost": cost
            },
            ignore_index=True
        )
    df.to_csv("publish/heuristic_models/la_base_experiment.csv")
