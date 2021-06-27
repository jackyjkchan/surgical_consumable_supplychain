from scm_optimization.integer_dual_balancing import DualBalancing
from random import random
from scm_optimization.model import *
from scipy.optimize import minimize, bisect, minimize_scalar
import pandas as pd
import pickle


class Hospital:
    def __init__(self, db_model, periods=20):
        self.db_model = db_model
        self.n_info = len(db_model.info_state_rvs) - 1
        self.periods = periods

        self.schedule = [0] + list(sum(self.db_model.info_state_rvs).rand(n=periods))
        self.demand = [db_model.usage_model.random(x) for x in self.schedule]

        self.order = [0] * (periods + 1)
        self.order_continuous = [0] * (periods + 1)
        self.inventory_level = [0] * (periods + 1)
        # self.inventory_position = [0] * (periods + 1)
        self.cost_incurred = 0
        self.backlog_cost_incurred = 0
        self.holding_cost_incurred = 0

        self.clock = 1

    def clock_to_time(self, clock):
        time = self.periods - clock
        return time

    def run(self):
        x = self.inventory_level[self.clock - 1]
        o = tuple(self.schedule[self.clock: self.clock + self.n_info])
        i_max = len(self.schedule)
        while self.clock < len(self.schedule):
            t = self.clock_to_time(self.clock)
            q = self.db_model.order_q_continuous(t, x, o)

            self.order_continuous[self.clock] = q
            order_q = int(q) if random() > q - int(q) else int(q) + 1
            self.order[self.clock] = order_q

            x += order_q - self.demand[self.clock]
            self.inventory_level[self.clock] = x

            self.cost_incurred += self.db_model.h * max([0, x]) - self.db_model.b * min([0, x])
            self.backlog_cost_incurred -= self.db_model.b * min([0, x])
            self.holding_cost_incurred += self.db_model.h * max([0, x])
            self.clock += 1

            o = tuple(self.schedule[self.clock: min([self.clock + self.n_info, i_max])])


if __name__ == "__main__":
    backlogging_cost = 1000
    infos = [1]

    gamma = 1
    lead_time = 0
    info = 0

    results = pd.DataFrame()
    holding_cost = 1

    setup_cost = 0
    unit_price = 0
    usage_model = PoissonUsageModel(scale=1)

    s = 3000

    for info in infos:
        results_fn = "db_results_b_{}_{}_r_{}.csv".format(str(backlogging_cost), str(info), str(s))
        info_state_rvs = [pacal.ConstDistr(0)] * info + \
                         [pacal.BinomialDistr(10, 0.5)]
        model = DualBalancing(gamma,
                              lead_time,
                              info_state_rvs,
                              holding_cost,
                              backlogging_cost,
                              setup_cost,
                              unit_price,
                              usage_model=usage_model)

        for i in range(s, s+1000):
            print("info: ", info, "rep: ", i)
            hospital = Hospital(db_model=model, periods=20)
            hospital.run()
            fn = "hospital_info{}_rep{}_b{}_r_{}.pickle".format(str(info), str(i), str(backlogging_cost), str(i))
            # pickle.dump(hospital, open(fn, 'wb'))
            results = results.append({
                "pickle": fn,
                "info": info,
                "rep": i,
                "cost": hospital.cost_incurred,
                "backlog_cost_incurred": hospital.backlog_cost_incurred,
                "holding_cost_incurred": hospital.holding_cost_incurred,
                "schedule": hospital.schedule,
                "order_cont": hospital.order_continuous,
                "order": hospital.order,
                "demand": hospital.demand,
                "inventory": hospital.inventory_level
            }, ignore_index=True)
            results.to_csv(results_fn)
