import math
import pacal
from collections import defaultdict
import itertools
import numpy
import time
import pandas as pd
from multiprocessing import Pool
from datetime import date, datetime

RV0 = pacal.ConstDistr(0)


class PoissonUsageModel:
    def __init__(self, scale=1, trunk=1e-3):
        self.scale = scale
        self.trunk = trunk

    def usage(self, o):
        return pacal.PoissonDistr(o*self.scale, trunk_eps=self.trunk)


class BinomUsageModel:
    def __init__(self, n=1, p=0.5):
        self.n = n
        self.p = p

    def usage(self, o):
        return pacal.BinomialDistr(int(o * self.n), p=self.p)


class DeterministUsageModel:
    def __init__(self, scale=1):
        self.scale = scale

    def usage(self, o):
        return pacal.ConstDistr(o*self.scale)



class ModelConfig:
    def __init__(self,
                 gamma=0.9,
                 lead_time=0,
                 info_state_rvs=[pacal.ConstDistr(0), pacal.ConstDistr(0)],
                 holding_cost=1,
                 backlogging_cost=10,
                 setup_cost=0,
                 unit_price=0,
                 increments=1,
                 horizon=None,
                 info_rv=None,
                 usage_model=PoissonUsageModel(scale=1),
                 label=None,
                 label_index=None):

        if horizon is not None and info_rv:
            if horizon == 0:
                info_state_rvs = [info_rv, RV0]
            else:
                info_state_rvs = [RV0] * horizon + [info_rv]

        self.label = label
        self.sub_label = "{}_{}_{}".format(date.today().isoformat(), label, str(label_index))
        self.results_fn = self.sub_label + ".pickle"

        self.params = dict(
            gamma=gamma,
            lead_time=lead_time,
            info_state_rvs=info_state_rvs,
            holding_cost=holding_cost,
            backlogging_cost=backlogging_cost,
            setup_cost=setup_cost,
            unit_price=unit_price,
            usage_model=usage_model,
            increments=increments,
            information_horizon=horizon
        )


class StationaryOptModel:
    def __init__(self,
                 gamma,
                 lead_time,
                 info_state_rvs,
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
        self.info_state_rvs = info_state_rvs
        self.increments = increments

        # usage_model = lambda o: pacal.BinomialDistr(o, p=0.5)
        # usage_model = lambda o: pacal.ConstDistr(o)
        # usage_model = usage_model=pacal.PoissonDistr
        default_usage_model = PoissonUsageModel(scale=1)
        self.usage_model = usage_model if usage_model else default_usage_model

        self.h = holding_cost
        self.b = backlogging_cost
        self.k = setup_cost
        self.c = unit_price

        # static list of possible info states
        self.info_states_cache = None

        self.value_function_j = {}
        self.value_function_v = {}
        self.value_function_v_argmin = {}
        self.base_stock_level_cache = {}
        self.current_demand_cache = {}
        self.reward_funcion_g_cache = {}

        unknown_lt_info = sum(self.info_state_rvs[i] for j in range(self.lead_time + 1) for i in range(j + 1))
        if len(unknown_lt_info.get_piecewise_pdf().getDiracs()) == 1:
            unknown_lt_info = unknown_lt_info.get_piecewise_pdf().getDiracs()[0].a
            if unknown_lt_info:
                self.unknown_lt_demand_rv = self.usage_model.usage(unknown_lt_info)
            else:
                self.unknown_lt_demand_rv = 0
        else:
            unknown_lt_demand_pdf = sum([dirac.f * self.usage_model.usage(dirac.a).get_piecewise_pdf()
                                         for dirac in unknown_lt_info.get_piecewise_pdf().getDiracs()
                                         ])
            self.unknown_lt_demand_rv = pacal.DiscreteDistr([dirac.a for dirac in unknown_lt_demand_pdf.getDiracs()],
                                                            [dirac.f for dirac in unknown_lt_demand_pdf.getDiracs()])

        if len(self.info_state_rvs[0].get_piecewise_pdf().getDiracs()) == 1:
            val = self.info_state_rvs[0].get_piecewise_pdf().getDiracs()[0].a
            if val:
                self.unknown_demand_rv = self.usage_model.usage(unknown_lt_info)
            else:
                self.unknown_demand_rv = 0
        else:
            unknown_demand_pdf = sum([dirac.f * self.usage_model.usage(dirac.a).get_piecewise_pdf()
                                      for dirac in unknown_lt_info.get_piecewise_pdf().getDiracs()
                                      ])
            self.unknown_demand_rv = pacal.DiscreteDistr([dirac.a for dirac in unknown_demand_pdf.getDiracs()],
                                                         [dirac.f for dirac in unknown_demand_pdf.getDiracs()])

    def info_states(self):
        if len(self.info_state_rvs) == 1:
            pass
        if self.info_states_cache:
            return self.info_states_cache
        else:
            info_vals = [[diracs.a for diracs in rv.get_piecewise_pdf().getDiracs()] for rv in self.info_state_rvs[1:]]
            info_state_comb = []
            for i in range(len(self.info_state_rvs) - 1):
                info_state_comb.append(list(sum(c) for c in itertools.product(*info_vals[i:])))
            info_states = list(itertools.product(*info_state_comb))
            self.info_states_cache = info_states
            return self.info_states_cache

    def lambda_t(self, o):
        return o[0] + self.info_state_rvs[-1]

    # # O_t^L in notation
    # def observed_lt_info(self, o):
    #     return sum(o[0: self.lead_time + 1])
    #
    # # U_t^L in notation
    # def unobserved_lt_info(self, o):
    #     return sum(self.info_state_rvs[self.lead_time:])
    #
    # # \Lambda_t^L in notation
    # def lt_info_state(self, o):
    #     return self.observed_lt_info(o) + self.unobserved_lt_info(o)

    # D_t^L | \Lambda_t in notation
    def lt_demand(self, o):
        s = time.time()
        known_demand_rv = self.usage_model.usage(sum(o[0:self.lead_time + 1])) \
            if sum(o[0:self.lead_time + 1]) else pacal.ConstDistr(0)

        lt_demand_rv = known_demand_rv
        if self.unknown_lt_demand_rv:
            lt_demand_rv += self.unknown_lt_demand_rv
        return lt_demand_rv

    # D_t | \Lambda_t in notation
    def current_demand(self, o):
        if o[0] in self.current_demand_cache:
            return self.current_demand_cache[o[0]]
        if self.unknown_demand_rv:
            current_demand = self.usage_model.usage(o[0]) + self.unknown_demand_rv
        else:
            current_demand = self.usage_model.usage(o[0])
        self.current_demand_cache[o[0]] = current_demand
        return current_demand

    # expected discounted holding and backlog cost at end of period t + L given action (target inventory position)
    # \tilde{G} in notation
    def G_future(self, y, o):
        x = y - self.lt_demand(o)
        h_cost = self.h * pacal.max(x, 0).mean()
        b_cost = -self.b * pacal.min(x, 0).mean()
        cost = h_cost + b_cost
        v = self.gamma ** self.lead_time * cost
        return v

    def G(self, y, o):
        lt_o = sum(o[0:self.lead_time + 1])
        if (y, lt_o) in self.reward_funcion_g_cache:
            return self.reward_funcion_g_cache[(y, lt_o)]
        self.reward_funcion_g_cache[(y, lt_o)] = (1 - self.gamma) * self.c * y + self.G_future(y, o)
        return self.reward_funcion_g_cache[(y, lt_o)]

    # state t is reversed, terminal stage is t=0 and starting stage is t=T
    # returns new state as random variables
    def state_transition(self, t, y, o):
        next_x = y - self.current_demand(o)
        next_o = [i + j for i, j in zip(self.info_state_rvs[1:], o[1:] + (0,))]
        return t - 1, next_x, next_o

    def unpack_state_transition(self, t, x_rv, o_rv):
        states = []
        probabilities = []

        x_diracs = x_rv.get_piecewise_pdf().getDiracs()
        o_diracs = [o.get_piecewise_pdf().getDiracs() for o in o_rv]

        o_combinations = list(itertools.product(*o_diracs))
        for next_x in x_diracs:
            for next_o in o_combinations:
                p = next_x.f * numpy.prod([info.f for info in next_o])
                states.append((t, next_x.a, tuple(info.a for info in next_o)))
                probabilities.append(p)
        return states, probabilities

    def j_function(self, t, x, o):
        if (t, x, o) in self.value_function_j:
            return self.value_function_j[(t, x, o)]
        elif t == -1:
            return 0
        else:
            # Exploit S s structure
            stock_up_lvl = self.stock_up_level(t, o)
            base_stock_lvl = self.base_stock_level(t, o)
            if x <= base_stock_lvl:
                j_value = self.k + self.v_function(t, float(stock_up_lvl), o)
            else:
                j_value = self.v_function(t, float(x), o)
            self.value_function_j[(t, x, o)] = j_value
            return j_value

    def base_stock_level(self, t, o):
        if (t, o) in self.base_stock_level_cache:
            return self.base_stock_level_cache[(t, o)]
        else:
            stock_up_level = self.stock_up_level(t, o)
            x = stock_up_level
            # while do nothing at inv pos x is better than do something, go to lower inv pos.
            while self.v_function(t, float(x), o) < self.v_function(t, float(stock_up_level), o) + self.k:
                x -= self.increments
            self.base_stock_level_cache[(t, o)] = x
            return x

    def stock_up_level(self, t, o):
        return self.v_function_argmin(t, o)

    def v_function_argmin(self, t, o):
        if (t, o) in self.value_function_v_argmin:
            return self.value_function_v_argmin[(t, o)]
        upper = self.v_function(t, 0, o)
        y_min = 0
        v_min = upper
        y = self.increments
        while self.v_function(t, float(y), o) <= v_min + self.k:
            v = self.v_function(t, float(y), o)
            if v < v_min:
                y_min = y
                v_min = v
            y += self.increments

        self.value_function_v_argmin[(t, o)] = y_min
        return y_min

    def v_function(self, t, y, o):
        if (t, y, o) in self.value_function_v:
            return self.value_function_v[(t, y, o)]
        next_t, next_x, next_o = self.state_transition(t, y, o)
        new_states, probabilities = self.unpack_state_transition(next_t, next_x, next_o)
        value = self.G(y, o) + self.gamma * sum(p * self.j_function(*state)
                                                for p, state in zip(probabilities, new_states))
        self.value_function_v[(t, y, o)] = value
        return value


def run_config(args):
    config, ts, xs = args
    results = pd.DataFrame(columns=['label',
                                    'usage_model',
                                    'info_rv',
                                    'gamma',
                                    'holding_cost',
                                    'backlogging_cost',
                                    'setup_cost',
                                    'unit_price',
                                    'information_horizon',
                                    'lead_time',
                                    't',
                                    'inventory_position_state',
                                    'information_state',
                                    'j_value_function',
                                    'base_stock',
                                    'order_up_to',
                                    'increments'])
    model = StationaryOptModel(config.params["gamma"],
                               config.params["lead_time"],
                               config.params["info_state_rvs"],
                               config.params["holding_cost"],
                               config.params["backlogging_cost"],
                               config.params["setup_cost"],
                               config.params["unit_price"],
                               increments=config.params["increments"],
                               usage_model=config.params["usage_model"])
    print("Starting {}: {}".format(config.sub_label, datetime.now().isoformat()))

    for t in ts:
        for x in xs:
            for o in model.info_states():
                j_value = model.j_function(t, x, o)
                base_stock = model.base_stock_level(t, o)
                stock_up = model.stock_up_level(t, o)

                result = dict(config.params)
                result.update({'label': config.label,
                               't': t,
                               'inventory_position_state': x,
                               'information_state': o,
                               'j_value_function': j_value,
                               'base_stock': base_stock,
                               'order_up_to': stock_up})
                results = results.append(result, ignore_index=True)
        results.to_pickle(config.results_fn)
    print("Finished {}: {}".format(config.sub_label, datetime.now().isoformat()))


def run_configs(configs, ts, xs, pools=4):
    print("Starting {} Runs: {}".format(str(len(configs)), datetime.now().isoformat()))
    p = Pool(pools)
    p.map(run_config, list((config, ts, xs) for config in configs))
    results = list(pd.read_pickle(config.results_fn) for config in configs)
    results = pd.concat(results)
    merged_fn = "{}_{}.pickle".format(date.today().isoformat(), configs[0].label)
    results.to_pickle(merged_fn)


if __name__ == "__main__":
    gamma = 0.9
    lead_time = 0
    horizon = 2
    info_state_rvs = [pacal.ConstDistr(0),
                      pacal.ConstDistr(0),
                      pacal.DiscreteDistr([1, 2, 19, 20], [0.25, 0.25, 0.25, 0.25])]
    holding_cost = 1
    backlogging_cost = 10
    setup_cost = 5
    unit_price = 0
    usage_model = PoissonUsageModel(scale=1)
    # usage_model = lambda o: pacal.ConstDistr(o)
    # usage_model = lambda o: pacal.PoissonDistr(o, trunk_eps=1e-3)
    # sage_model = None
    model = StationaryOptModel(gamma,
                               lead_time,
                               horizon,
                               info_state_rvs,
                               holding_cost,
                               backlogging_cost,
                               setup_cost,
                               unit_price,
                               usage_model=usage_model)

    # t, x, o = model.state_transition(10, 10, (3, 2))

    s = time.time()
    print(model.j_function(1, 0, (3, 2)))
    print("run time:", time.time() - s)
    s = time.time()
    print(model.j_function(2, 0, (3, 2)))
    print("run time:", time.time() - s)
    s = time.time()
    print(model.j_function(3, 0, (3, 2)))
    print("run time:", time.time() - s)
    s = time.time()
    print(model.j_function(4, 0, (3, 2)))
    print("run time:", time.time() - s)
    s = time.time()
    print(model.j_function(5, 0, (3, 2)))
    print("run time:", time.time() - s)
    s = time.time()

    # print(model.value_function_j)
    # print(model.value_function_v)
    # print(model.v_function(0, 3, (3, 2)))
    # print(model.v_function(0, 4, (3, 2)))
    # print(model.v_function(0, 5, (3, 2)))
    # print(model.v_function(0, 6, (3, 2)))
    # print(model.v_function(0, 7, (3, 2)))
    # print(model.v_function(0, 8, (3, 2)))
