import pickle
import pandas as pd

t = 20
x = 0

results = pd.DataFrame()

binomial_ns = [3, 4, 5, 10]
infos = [0, 1, 2]

for binomial_n in binomial_ns:
    for info in infos:

        try:
            with open(f"la_binomial_models/LA_Model_b_1000_info_{info}_binomial_usage_{binomial_n}_t_20_model.pickle", "rb") as f:
                model = pickle.load(f)

            value = 0
            for o in model.info_states_prob_cache:
                value += model.info_states_prob_cache[o] * model.value_function_j[(t, x, o)]

            results = results.append({"binomial_n": binomial_n, "info": info, "cost": value}, ignore_index=True)
            print({"binomial_n": binomial_n, "info": info, "cost": value})
        except:
            print("not found:", binomial_n, info)
            pass

print(results)