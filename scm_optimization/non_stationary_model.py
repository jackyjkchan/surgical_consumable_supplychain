from scm_optimization.model import *
import pacal
import math
import os
import itertools
import numpy
import time
import pandas as pd
import pickle

from multiprocessing import Pool
from datetime import date, datetime


class ModelConfig:
    def __init__(self,
                 gamma=0.9,
                 lead_time=0,
                 ns_info_state_rvs=[[pacal.ConstDistr(0), pacal.ConstDistr(0)]],
                 holding_cost=1,
                 backlogging_cost=10,
                 setup_cost=0,
                 unit_price=0,
                 elective_info_state_rv=None,
                 emergency_info_state_rv=None,
                 info_horizon=None,
                 increments=1,
                 usage_model=PoissonUsageModel(scale=1),
                 label=None,
                 label_index=None):

        if elective_info_state_rv and emergency_info_state_rv:
            ns_info_state_rvs = []
            # 0..4 Weekdays, 5, 6 weekdays
            for rt in range(7):
                info_state_rv = []
                t_rt = (rt + info_horizon) % 7
                info_state_rv = [emergency_info_state_rv] + [pacal.ConstDistr(0)] * info_horizon
                if t_rt not in [5, 6]:
                    info_state_rv[-1] += elective_info_state_rv
                ns_info_state_rvs.append(info_state_rv)

        print(ns_info_state_rvs)

        self.label = label
        self.sub_label = "{}_{}_{}".format(date.today().isoformat(), label, str(label_index))
        self.results_fn = self.sub_label + ".pickle"

        self.params = dict(
            gamma=gamma,
            lead_time=lead_time,
            ns_info_state_rvs=ns_info_state_rvs,
            holding_cost=holding_cost,
            backlogging_cost=backlogging_cost,
            setup_cost=setup_cost,
            unit_price=unit_price,
            usage_model=usage_model,
            increments=increments,
            information_horizon=info_horizon
        )


def run_config(args):
    config, ts, xs = args
    results = pd.DataFrame(columns=['label',
                                    'usage_model',
                                    'gamma',
                                    'holding_cost',
                                    'backlogging_cost',
                                    'setup_cost',
                                    'unit_price',
                                    'lead_time',
                                    't',
                                    'inventory_position_state',
                                    'information_state',
                                    'j_value_function',
                                    'base_stock',
                                    'order_up_to',
                                    'increments'])
    model = NonStationaryOptModel(config.params["gamma"],
                                  config.params["lead_time"],
                                  config.params["ns_info_state_rvs"],
                                  config.params["holding_cost"],
                                  config.params["backlogging_cost"],
                                  config.params["setup_cost"],
                                  config.params["unit_price"],
                                  increments=config.params["increments"],
                                  usage_model=config.params["usage_model"])
    print("Starting {}: {}".format(config.sub_label, datetime.now().isoformat()))

    for t in ts:
        rt = model.rt(t)
        for x in xs:
            for o in model.info_states()[rt]:

                j_value = model.j_function(t, x, o)
                print(t, x, o, j_value)
                j_k = model.j_function_k(t, x, o)
                j_b = model.j_function_b(t, x, o)
                j_h = model.j_function_h(t, x, o)
                j_p = model.j_function_p(t, x, o)
                base_stock = model.base_stock_level(t, o)
                stock_up = model.stock_up_level(t, o)

                result = dict(config.params)
                result.update({'label': config.label,
                               't': t,
                               'inventory_position_state': x,
                               'information_state': o,
                               'j_value_function': j_value,
                               'j_k': j_k,
                               'j_b': j_b,
                               'j_h': j_h,
                               'j_p': j_p,
                               'base_stock': base_stock,
                               'order_up_to': stock_up})
                results = results.append(result, ignore_index=True)
        results.to_pickle(config.results_fn)
    print("Finished {}: {}".format(config.sub_label, datetime.now().isoformat()))
    if not os.path.exists("{}_{}".format(date.today().isoformat(), config.label)):
        os.mkdir("{}_{}".format(date.today().isoformat(), config.label))
    model.to_pickle("{}_{}/{}".format(date.today().isoformat(), config.label, config.sub_label))


def run_configs(configs, ts, xs, pools=4):
    print("Starting {} Runs: {}".format(str(len(configs)), datetime.now().isoformat()))
    p = Pool(pools)
    p.map(run_config, list((config, ts, xs) for config in configs))
    results = list(pd.read_pickle(config.results_fn) for config in configs)
    results = pd.concat(results)
    merged_fn = "{}_{}.pickle".format(date.today().isoformat(), configs[0].label)
    results.to_pickle(merged_fn)
    for config in configs:
        os.remove(config.results_fn)


class NonStationaryOptModel(StationaryOptModel):
    """
    Non-Stationary info_state_rvs model. Everything else is still stationary.
    info_state_rvs_list is now a list of info_state_rvs. This list should ordered wrt real time, rt.
    0 - Monday, 1 - Tuesday... 7 - Sunday
    t in this model will be the same as in the StationaryOptModel.
    rt (real time) will be used to index into non-stationary lists
    rt = - t - 1
    so when t=0 (last decision), rt=-1 (start from last element of non-stationary lists.
    """

    def __init__(self,
                 gamma,
                 lead_time,
                 ns_info_state_rvs,
                 holding_cost,
                 backlogging_cost,
                 setup_cost,
                 unit_price,
                 usage_model=None,
                 increments=1
                 ):

        # parameters in order:
        # single period discount factor
        # lead time for items to arrive, >= 0
        # information horizon N >= 0, N = 0 for no advanced information
        # vector of random variables, transition of the state of advanced information, M_{t, s} in notation

        self.gamma = gamma
        self.lead_time = lead_time
        self.ns_info_state_rvs = ns_info_state_rvs
        self.period = len(ns_info_state_rvs)
        self.info_horizon = max(self.lead_time, len(ns_info_state_rvs[0]))
        self.increments = increments

        # usage_model = lambda o: pacal.BinomialDistr(o, p=0.5)
        # usage_model = lambda o: pacal.ConstDistr(o)
        # usage_model = usage_model=pacal.PoissonDistr
        default_usage_model = PoissonUsageModel(scale=1)
        self.usage_model = usage_model if usage_model else default_usage_model
        self.ns_unknown_lt_demand_rvs = []
        self.ns_unknown_demand_rvs = []

        self.h = holding_cost
        self.b = backlogging_cost
        self.k = setup_cost
        self.c = unit_price

        # static list of possible info states
        self.info_states_cache = None

        # all caches
        self.value_function_j = {}
        self.j_h = {}
        self.j_b = {}
        self.j_k = {}
        self.j_p = {}

        self.value_function_v = {}
        self.v_h = {}
        self.v_b = {}
        self.v_k = {}
        self.v_p = {}

        self.value_function_v_argmin = {}
        self.base_stock_level_cache = {}
        self.current_demand_cache = {}

        self.reward_funcion_g_cache = {}
        self.g_h = {}
        self.g_b = {}
        self.g_p = {}

        ### Apppend Const(0) to info_state_rvs if leadtime > info_horizon
        if len(self.ns_info_state_rvs[0]) < self.lead_time + 1:
            diff = self.lead_time - len(self.ns_info_state_rvs[0]) + 1
            self.ns_info_state_rvs = list(info_state_rvs + diff * [pacal.ConstDistr(0)]
                                          for info_state_rvs in self.ns_info_state_rvs)

        for k in range(self.period):
            unknown_lt_info_rv = sum(self.ns_info_state_rvs[(j + k) % self.period][(i + k) % self.info_horizon]
                                     for j in range(self.lead_time + 1) for i in range(j + 1))
            if len(unknown_lt_info_rv.get_piecewise_pdf().getDiracs()) == 1:
                v = unknown_lt_info_rv.get_piecewise_pdf().getDiracs()[0].a
                self.ns_unknown_lt_demand_rvs.append(self.usage_model.usage(v) if v else pacal.ConstDistr(0))
            else:
                unknown_lt_demand_pdf = sum([dirac.f * self.usage_model.usage(dirac.a).get_piecewise_pdf()
                                             for dirac in unknown_lt_info_rv.get_piecewise_pdf().getDiracs()])
                unknown_lt_demand_rv = pacal.DiscreteDistr([dirac.a for dirac in unknown_lt_demand_pdf.getDiracs()],
                                                           [dirac.f for dirac in unknown_lt_demand_pdf.getDiracs()])
                self.ns_unknown_lt_demand_rvs.append(unknown_lt_demand_rv)

        for k in range(self.period):
            unknown_info_rv = self.ns_info_state_rvs[k][0]
            if len(unknown_info_rv.get_piecewise_pdf().getDiracs()) == 1:
                val = unknown_info_rv.get_piecewise_pdf().getDiracs()[0].a
                self.ns_unknown_demand_rvs.append(self.usage_model.usage(val) if val else pacal.ConstDistr(0))
            else:
                unknown_demand_pdf = sum([dirac.f * self.usage_model.usage(dirac.a).get_piecewise_pdf()
                                          for dirac in unknown_info_rv.get_piecewise_pdf().getDiracs()])
                unknown_demand_rv = pacal.DiscreteDistr([dirac.a for dirac in unknown_demand_pdf.getDiracs()],
                                                        [dirac.f for dirac in unknown_demand_pdf.getDiracs()])
                self.ns_unknown_demand_rvs.append(unknown_demand_rv)

    def rt(self, t):
        return (- t - 1) % self.period

    def lt_demand(self, rt, lt_o):
        lt_demand_rv = self.usage_model.usage(lt_o) if lt_o else pacal.ConstDistr(0)
        if self.ns_unknown_lt_demand_rvs[rt]:
            lt_demand_rv += self.ns_unknown_lt_demand_rvs[rt]
        return lt_demand_rv

    def current_demand(self, rt, o):
        if (rt, o[0]) in self.current_demand_cache:
            return self.current_demand_cache[(rt, o[0])]
        if self.ns_unknown_demand_rvs[rt]:
            current_demand = self.usage_model.usage(o[0]) + self.ns_unknown_demand_rvs[rt]
        else:
            current_demand = self.usage_model.usage(o[0])
        self.current_demand_cache[(rt, o[0])] = current_demand
        return current_demand

    def info_states(self):
        if self.info_states_cache:
            return self.info_states_cache
        info_horizon = len(self.ns_info_state_rvs[0])
        info_states_list = []
        for k in range(self.period):
            info_states = []
            for o in range(info_horizon - 1):
                relevant_rvs = [self.ns_info_state_rvs[(k - i) % self.period][i] for i in range(1, info_horizon - o)]
                info_vals = [[diracs.a for diracs in rv.get_piecewise_pdf().getDiracs()] for rv in relevant_rvs]
                info_states.append(set(sum(c) for c in itertools.product(*info_vals)))
            info_states_list.append(list(itertools.product(*info_states)))
        self.info_states_cache = info_states_list
        return self.info_states_cache

    def state_transition(self, t, y, o):
        rt = self.rt(t)
        next_x = y - self.current_demand(rt, o)
        next_o = [i + j for i, j in zip(self.ns_info_state_rvs[rt][1:], o[1:] + (0,))]
        return t - 1, next_x, next_o

    def G_future(self, rt, y, lt_o):
        x = y - self.lt_demand(rt, lt_o)
        h_cost = self.h * pacal.max(x, 0).mean()
        b_cost = -self.b * pacal.min(x, 0).mean()
        cost = h_cost + b_cost
        v = self.gamma ** self.lead_time * cost

        self.g_b[(rt, y, lt_o)] = self.gamma ** self.lead_time * b_cost
        self.g_h[(rt, y, lt_o)] = self.gamma ** self.lead_time * h_cost
        return v

    def G_b(self, rt, y, o):
        self.G(rt, y, o)
        lt_o = sum(o[0:self.lead_time + 1])
        return self.g_b[(rt, y, lt_o)]

    def G_h(self, rt, y, o):
        self.G(rt, y, o)
        lt_o = sum(o[0:self.lead_time + 1])
        return self.g_h[(rt, y, lt_o)]

    def G_p(self, rt, y, o):
        self.G(rt, y, o)
        lt_o = sum(o[0:self.lead_time + 1])
        return self.g_p[(rt, y, lt_o)]

    def G(self, rt, y, o):
        lt_o = sum(o[0:self.lead_time + 1])
        if (rt, y, lt_o) in self.reward_funcion_g_cache:
            return self.reward_funcion_g_cache[(rt, y, lt_o)]

        self.reward_funcion_g_cache[(rt, y, lt_o)] = (1 - self.gamma) * self.c * y + self.G_future(rt, y, lt_o)
        self.g_p[(rt, y, lt_o)] = (1 - self.gamma) * self.c * y
        return self.reward_funcion_g_cache[(rt, y, lt_o)]

    def v_function(self, t, y, o):
        rt = self.rt(t)
        if (t, y, o) in self.value_function_v:
            return self.value_function_v[(t, y, o)]
        next_t, next_x, next_o = self.state_transition(t, y, o)
        new_states, probabilities = self.unpack_state_transition(next_t, next_x, next_o)
        value = self.G(rt, y, o) + self.gamma * sum(p * self.j_function(*state)
                                                    for p, state in zip(probabilities, new_states))

        self.v_b[(t, y, o)] = self.G_b(rt, y, o) + self.gamma * sum(p * self.j_function_b(*state)
                                                                    for p, state in zip(probabilities, new_states))
        self.v_h[(t, y, o)] = self.G_h(rt, y, o) + self.gamma * sum(p * self.j_function_h(*state)
                                                                    for p, state in zip(probabilities, new_states))
        self.v_p[(t, y, o)] = self.G_p(rt, y, o) + self.gamma * sum(p * self.j_function_p(*state)
                                                                    for p, state in zip(probabilities, new_states))
        self.v_k[(t, y, o)] = self.gamma * sum(p * self.j_function_k(*state)
                                               for p, state in zip(probabilities, new_states))
        self.value_function_v[(t, y, o)] = value
        return value
