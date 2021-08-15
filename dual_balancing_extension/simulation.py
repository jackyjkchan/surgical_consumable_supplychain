from scm_optimization.integer_dual_balancing import DualBalancing
from random import random
from scm_optimization.model import *
from scipy.optimize import minimize, bisect, minimize_scalar
import pandas as pd
import pickle
import glob

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


class Hospital_LA:
    def __init__(self, model, periods=20):
        self.model = model
        self.n_info = len(model.info_state_rvs) - 1
        self.periods = periods

        self.schedule = [0] + list(sum(self.model.info_state_rvs).rand(n=periods))
        self.demand = [model.usage_model.random(x) for x in self.schedule]

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
            order_q = self.model.order_la (t, x, o)
            self.order[self.clock] = order_q

            x += order_q - self.demand[self.clock]
            self.inventory_level[self.clock] = x

            self.cost_incurred += self.model.h * max([0, x]) - self.model.b * min([0, x])
            self.backlog_cost_incurred -= self.model.b * min([0, x])
            self.holding_cost_incurred += self.model.h * max([0, x])
            self.clock += 1
            o = tuple(self.schedule[self.clock: min([self.clock + self.n_info, i_max])])


class Hospital_LA_MDP:
    def __init__(self, la_model, periods=21):
        mdps = {
            (10, 1, 0): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_0_model.pickle',
            (10, 1, 1): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_4_model.pickle',
            (10, 1, 2): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_8_model.pickle',
            (10, 1, 3): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_12_model.pickle',
            (100, 1, 0): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_1_model.pickle',
            (100, 1, 1): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_5_model.pickle',
            (100, 1, 2): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_9_model.pickle',
            (100, 1, 3): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_13_model.pickle',
            (1000, 1, 0): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_2_model.pickle',
            (1000, 1, 1): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_6_model.pickle',
            (1000, 1, 2): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_10_model.pickle',
            (1000, 1, 3): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_14_model.pickle',
            (10000, 1, 0): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_3_model.pickle',
            (10000, 1, 1): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_7_model.pickle',
            (10000, 1, 2): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_11_model.pickle',
            (10000, 1, 3): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_15_model.pickle'}
        # for pkl in glob.glob("2021-08-07_base_experiment_1e-3/*"):
        #     mdp_model = pickle.load(open(pkl, "rb"))
        #     mdp_info = len(mdp_model.info_state_rvs) - 1 if str(mdp_model.info_state_rvs[-1]) != '0' else 0
        #     mdps[(mdp_model.b, mdp_model.h, mdp_info)] = pkl
        # print(mdps)

        self.la_model = la_model

        self.b = la_model.b
        self.h = la_model.h
        self.n_info = len(la_model.info_state_rvs) - 1

        self.mdp_model = pickle.load(open(mdps[(self.b, self.h, self.n_info)], 'rb'))

        self.periods = periods

        self.schedule = [0] + list(sum(self.la_model.info_state_rvs).rand(n=periods))
        self.demand = [la_model.usage_model.random(x) for x in self.schedule]

        self.order_la = [0] * (periods + 1)
        self.order_mdp = [0] * (periods + 1)
        self.order_up_to_mdp = [0] * (periods + 1)

        self.inventory_level_la = [0] * (periods + 1)
        self.inventory_level_mdp = [0] * (periods + 1)
        # self.inventory_position = [0] * (periods + 1)
        self.cost_incurred_la = 0
        self.backlog_cost_incurred_la = 0
        self.holding_cost_incurred_la = 0

        self.cost_incurred_mdp = 0
        self.backlog_cost_incurred_mdp = 0
        self.holding_cost_incurred_mdp = 0

        self.clock = 1

    def clock_to_time(self, clock):
        time = self.periods - clock
        return time

    def run(self):
        x_la = self.inventory_level_la[self.clock - 1]
        x_mdp = self.inventory_level_mdp[self.clock - 1]

        o = tuple(self.schedule[self.clock: self.clock + self.n_info])
        i_max = len(self.schedule)
        while self.clock < len(self.schedule):
            mdp_o = o if len(o) == self.n_info else o + (0,) * (self.n_info - len(o))
            mdp_o = mdp_o if len(mdp_o) else (0,)
            
            mdp_t = self.periods - self.clock
            t = self.clock_to_time(self.clock)

            order_up_to = int(self.mdp_model.v_function_argmin(mdp_t, mdp_o))
            print("order_up_to: ", order_up_to)
            order_q = self.la_model.order_la(t, x_la, o)

            self.order_la[self.clock] = order_q

            order_up_to = int(self.mdp_model.v_function_argmin(mdp_t, mdp_o))
            order_mdp = int(max([0, order_up_to - x_mdp]))
            self.order_up_to_mdp[self.clock] = order_up_to
            self.order_mdp[self.clock] = order_mdp

            x_la += order_q - self.demand[self.clock]
            self.inventory_level_la[self.clock] = x_la

            x_mdp += order_mdp - self.demand[self.clock]
            self.inventory_level_mdp[self.clock] = x_mdp

            self.cost_incurred_la += self.la_model.h * max([0, x_la]) - self.la_model.b * min([0, x_la])
            self.backlog_cost_incurred_la -= self.la_model.b * min([0, x_la])
            self.holding_cost_incurred_la += self.la_model.h * max([0, x_la])

            self.cost_incurred_mdp += self.la_model.h * max([0, x_mdp]) - self.la_model.b * min([0, x_mdp])
            self.backlog_cost_incurred_mdp -= self.la_model.b * min([0, x_mdp])
            self.holding_cost_incurred_mdp += self.la_model.h * max([0, x_mdp])

            self.clock += 1
            o = tuple(self.schedule[self.clock: min([self.clock + self.n_info, i_max])])

            print("schedule: ", self.schedule)
            print("demand: ", self.demand)
            print("order_la: ", self.order_la)
            print("order_mdp: ", self.order_mdp)
            print("inventory_level_la: ", self.inventory_level_la)
            print("inventory_level_mdp: ", self.inventory_level_mdp)


class Hospital_DB_MDP:
    def __init__(self, db_model, periods=21):
        mdps = {
            (10, 1, 0): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_0_model.pickle',
            (10, 1, 1): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_4_model.pickle',
            (10, 1, 2): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_8_model.pickle',
            (10, 1, 3): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_12_model.pickle',
            (100, 1, 0): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_1_model.pickle',
            (100, 1, 1): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_5_model.pickle',
            (100, 1, 2): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_9_model.pickle',
            (100, 1, 3): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_13_model.pickle',
            (1000, 1, 0): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_2_model.pickle',
            (1000, 1, 1): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_6_model.pickle',
            (1000, 1, 2): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_10_model.pickle',
            (1000, 1, 3): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_14_model.pickle',
            (10000, 1, 0): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_3_model.pickle',
            (10000, 1, 1): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_7_model.pickle',
            (10000, 1, 2): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_11_model.pickle',
            (10000, 1, 3): '2021-08-07_base_experiment_1e-3/2021-08-07_base_experiment_detailed_1e-3_15_model.pickle'}
        # for pkl in glob.glob("2021-08-07_base_experiment_1e-3/*"):
        #     mdp_model = pickle.load(open(pkl, "rb"))
        #     mdp_info = len(mdp_model.info_state_rvs) - 1 if str(mdp_model.info_state_rvs[-1]) != '0' else 0
        #     mdps[(mdp_model.b, mdp_model.h, mdp_info)] = pkl
        # print(mdps)

        self.db_model = db_model

        self.b = db_model.b
        self.h = db_model.h
        self.n_info = len(db_model.info_state_rvs) - 1

        self.mdp_model = pickle.load(open(mdps[(self.b, self.h, self.n_info)], 'rb'))

        self.periods = periods

        self.schedule = [0] + list(sum(self.db_model.info_state_rvs).rand(n=periods))
        self.demand = [db_model.usage_model.random(x) for x in self.schedule]

        self.order_db = [0] * (periods + 1)
        self.order_mdp = [0] * (periods + 1)
        self.order_up_to_mdp = [0] * (periods + 1)

        self.inventory_level_db = [0] * (periods + 1)
        self.inventory_level_mdp = [0] * (periods + 1)
        # self.inventory_position = [0] * (periods + 1)
        self.cost_incurred_db = 0
        self.backlog_cost_incurred_db = 0
        self.holding_cost_incurred_db = 0

        self.cost_incurred_mdp = 0
        self.backlog_cost_incurred_mdp = 0
        self.holding_cost_incurred_mdp = 0

        self.clock = 1

    def clock_to_time(self, clock):
        time = self.periods - clock
        return time

    def run(self):
        x_db = self.inventory_level_db[self.clock - 1]
        x_mdp = self.inventory_level_mdp[self.clock - 1]

        o = tuple(self.schedule[self.clock: self.clock + self.n_info])
        i_max = len(self.schedule)
        while self.clock < len(self.schedule):
            mdp_o = o if len(o) == self.n_info else o + (0,) * (self.n_info - len(o))
            mdp_o = mdp_o if len(mdp_o) else (0,)

            mdp_t = self.periods - self.clock
            t = self.clock_to_time(self.clock)

            order_up_to = int(self.mdp_model.v_function_argmin(mdp_t, mdp_o))
            print("order_up_to: ", order_up_to)
            q = self.db_model.order_q_continuous(t, x_db, o)
            order_db = int(q) if random() > q - int(q) else int(q) + 1

            self.order_db[self.clock] = order_db

            order_up_to = int(self.mdp_model.v_function_argmin(mdp_t, mdp_o))
            order_mdp = int(max([0, order_up_to - x_mdp]))
            self.order_up_to_mdp[self.clock] = order_up_to
            self.order_mdp[self.clock] = order_mdp

            x_db += order_db - self.demand[self.clock]
            self.inventory_level_db[self.clock] = x_db

            x_mdp += order_mdp - self.demand[self.clock]
            self.inventory_level_mdp[self.clock] = x_mdp

            self.cost_incurred_db += self.db_model.h * max([0, x_db]) - self.db_model.b * min([0, x_db])
            self.backlog_cost_incurred_db -= self.db_model.b * min([0, x_db])
            self.holding_cost_incurred_db += self.db_model.h * max([0, x_db])

            self.cost_incurred_mdp += self.db_model.h * max([0, x_mdp]) - self.db_model.b * min([0, x_mdp])
            self.backlog_cost_incurred_mdp -= self.db_model.b * min([0, x_mdp])
            self.holding_cost_incurred_mdp += self.db_model.h * max([0, x_mdp])

            self.clock += 1
            o = tuple(self.schedule[self.clock: min([self.clock + self.n_info, i_max])])

            print("schedule: ", self.schedule)
            print("demand: ", self.demand)
            print("order_db: ", self.order_db)
            print("order_mdp: ", self.order_mdp)
            print("inventory_level_db: ", self.inventory_level_db)
            print("inventory_level_mdp: ", self.inventory_level_mdp)


if __name__ == "__main__":



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

    print("backlogging cost:", backlogging_cost, " info: ", info, " rep: ", rep)

    hospital = Hospital_LA_MDP(la_model=model, periods=21)
    hospital.run()

    result = {
        "info": info,
        "backlogging_cost": backlogging_cost,
        "rep": rep,
        "cost_la": hospital.cost_incurred_la,
        "backlog_cost_incurred_la": hospital.backlog_cost_incurred_la,
        "holding_cost_incurred_la": hospital.holding_cost_incurred_la,

        "cost_mdp": hospital.cost_incurred_mdp,
        "backlog_cost_incurred_mdp": hospital.backlog_cost_incurred_mdp,
        "holding_cost_incurred_mdp": hospital.holding_cost_incurred_mdp,

        "schedule": hospital.schedule,
        "demand": hospital.demand,
        "order_la": hospital.order_la,
        "inventory_la": hospital.inventory_level_la,
        "order_mdp": hospital.order_mdp,
        "order_upto": hospital.order_up_to_mdp,
        "inventory_mdp": hospital.inventory_level_mdp,

        "run_time_min": (time.time() - start_time)/60
    }
