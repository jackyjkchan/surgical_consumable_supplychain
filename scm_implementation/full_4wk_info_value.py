import scm_optimization.non_stationary_model as ns_model
from scm_optimization.non_stationary_model import NonStationaryOptModel
from datetime import date, datetime
from scm_optimization.model import DeterministUsageModel, BinomUsageModel, PoissonUsageModel
from scm_implementation.ns_info_state_rvs.ns_info_state_rvs import elective_info_rvs, emergency_info_rvs
import pandas as pd
import numpy as np
import pacal
import os
import pickle
from multiprocessing import Pool
import json
import time


def run_model_info(arg):
    model, info = arg
    for t in range(28):
        x = 0
        o_t = info[-t - 1:] + tuple([0] * (28 - t - 1))
        j_value = model.j_function(t, x, o_t)
    return j_value


def gen_scenario(rv):
    return tuple(rv.rand(5)) + (0, 0) + \
           tuple(rv.rand(5)) + (0, 0) + \
           tuple(rv.rand(5)) + (0, 0) + \
           tuple(rv.rand(5)) + (0, 0)


if __name__ == "__main__":
    # case study items, 47320, 56931, 1686, 129636, 83532, 38262
    repetitions = 100
    configs = []
    item_ids = [id for id in elective_info_rvs]
    data = pd.DataFrame()

    for item_id in ["47320", "56931", "1686", "129636", "83532", "38262"]:
    #for item_id in ["47320"]:
        for b in [1000, 10000]:
        #for b in [100]:
            for lt in [0, 1]:
            #for lt in [1]:
                config = ns_model.ModelConfig(gamma=1,
                                              lead_time=lt,
                                              holding_cost=1,
                                              backlogging_cost=b,
                                              setup_cost=0,
                                              unit_price=0,
                                              usage_model=PoissonUsageModel(scale=1),
                                              elective_info_state_rv=pacal.ConstDistr(0),
                                              emergency_info_state_rv=emergency_info_rvs[item_id],
                                              horizon=28,
                                              label="ns_impl_full_value_{}".format(item_id),
                                              label_index=0
                                              )

                results = []
                start = datetime.now()
                duration = 0

                model_args = (config.params["gamma"],
                              config.params["lead_time"],
                              config.params["ns_info_state_rvs"],
                              config.params["holding_cost"],
                              config.params["backlogging_cost"],
                              config.params["setup_cost"],
                              config.params["unit_price"])
                model = NonStationaryOptModel(*model_args)

                p = Pool(8)

                models = list(NonStationaryOptModel(*model_args) for _ in range(repetitions))
                info_scenarios = list(gen_scenario(elective_info_rvs[item_id]) for _ in range(repetitions))
                results = p.map(run_model_info, zip(models, info_scenarios))
                mean = np.mean(results)
                stddev = np.std(results, ddof=1)
                half_width = 1.96*stddev/np.sqrt(repetitions)

                summary = {
                    "item_id": item_id,
                    "backlogging_cost": b,
                    "lead_time": lt,
                    "mean": mean,
                    "stddev": stddev,
                    "half_width": half_width,
                    "upper": mean+half_width,
                    "lower": mean-half_width
                }
                data = data.append(summary, ignore_index=True)
                data.to_csv("full_value_info_cost_4wks_{0:}_b_{1:}_lt_{2:}.csv".format(item_id, str(b), str(lt)),
                            index=False)

                # with open("full_info_{0:}_b_{1:}_lt_{2:}_raw.txt".format(item_id, str(b), str(lt)), "w") as f:
                #     for r in results:
                #         f.write(str(r))
                #         f.write("\n")
                time.sleep(1)

                # with open("full_info_{0:}_b_{1:}_lt_{2:}_raw.txt".format(item_id, str(b), str(lt)), "w") as f:
                #     json.dump(summary, fp)


