import math
import os
import pacal
import itertools
import numpy
import time
import pandas as pd
import pickle

from multiprocessing import Pool
from datetime import date, datetime

RV0 = pacal.ConstDistr(0)


def rv_str(rv):
    return str(rv)[0:str(rv).find("#")]


class UsageModel:
    def __lt__(self, other):
        if self.name < other.name:
            return True
        else:
            return False

    def __eq__(self, other):
        if self.name == other.name:
            return True
        else:
            return False

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name


class PoissonUsageModel(UsageModel):
    def __init__(self, scale=1, trunk=1e-5):
        self.name = "Poisson {} {}".format(str(scale), str(trunk))
        self.scale = scale
        self.trunk = trunk

    def usage(self, o):
        return pacal.PoissonDistr(o * self.scale, trunk_eps=self.trunk)

    def random(self, o=1):
        fail = True
        while fail:
            try:
                x = self.usage(o).rand(1)[0]
                fail = False
            except:
                fail = True
        return x
        #return numpy.random.poisson(o * self.scale)


class BinomUsageModel(UsageModel):
    def __init__(self, n=1, p=0.5):
        self.name = "Binom {} {}".format(str(n), str(p))
        self.n = n
        self.p = p
        self.trunk = 1e-5

    def usage(self, o):
        return pacal.BinomialDistr(int(o * self.n), p=self.p)

    def random(self, o=1):
        return numpy.random.binomial(o * self.n, self.p)


class DeterministUsageModel(UsageModel):
    def __init__(self, scale=1):
        self.name = "Const {}".format(str(scale))
        self.scale = scale

    def usage(self, o):
        return pacal.ConstDistr(o * self.scale)

    def random(self, o=1):
        return o * self.scale


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
                 detailed=False,
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
        self.detailed = detailed

        self.params = dict(
            gamma=gamma,
            lead_time=lead_time,
            info_state_rvs=info_state_rvs,
            info_rv=info_rv,
            info_rv_str=rv_str(info_rv) if info_rv else None,
            holding_cost=holding_cost,
            backlogging_cost=backlogging_cost,
            setup_cost=setup_cost,
            unit_price=unit_price,
            usage_model=usage_model,
            increments=increments,
            information_horizon=horizon,
            detailed=detailed
        )


class StationaryOptModel:

    @classmethod
    def read_pickle(cls, filename):
        with open(filename, "rb") as f:
            m = pickle.load(f)
        return m

    def __init__(self,
                 gamma,
                 lead_time,
                 info_state_rvs,
                 holding_cost,
                 backlogging_cost,
                 setup_cost,
                 unit_price,
                 usage_model=None,
                 increments=1,
                 detailed=False
                 ):

        # parameters in order:
        # single period discount factor
        # lead time for items to arrive, >= 0
        # information horizon N >= 0, N = 0 for no advanced information
        # vector of random variables, transition of the state of advanced information, M_{t, s} in notation
        self.detailed = detailed
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
        self.info_states_prob_cache = {}

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
        if len(self.info_state_rvs) < self.lead_time + 1:
            diff = self.lead_time - len(self.info_state_rvs) + 1
            self.info_state_rvs = self.info_state_rvs + diff * [pacal.ConstDistr(0)]

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

        unknown_info = self.info_state_rvs[0]
        if len(unknown_info.get_piecewise_pdf().getDiracs()) == 1:
            val = self.info_state_rvs[0].get_piecewise_pdf().getDiracs()[0].a
            if val:
                self.unknown_demand_rv = self.usage_model.usage(val)
            else:
                self.unknown_demand_rv = 0
        else:
            unknown_demand_pdf = sum([dirac.f * self.usage_model.usage(dirac.a).get_piecewise_pdf()
                                      for dirac in unknown_info.get_piecewise_pdf().getDiracs()
                                      ])
            self.unknown_demand_rv = pacal.DiscreteDistr([dirac.a for dirac in unknown_demand_pdf.getDiracs()],
                                                         [dirac.f for dirac in unknown_demand_pdf.getDiracs()])
        self.info_states()


    def info_states(self):
        if len(self.info_state_rvs) == 1:
            pass
        if self.info_states_cache:
            return self.info_states_cache
        else:
            info_vals = [[diracs.a for diracs in rv.get_piecewise_pdf().getDiracs()] for rv in self.info_state_rvs[1:]]
            info_vals_p = [[diracs.f for diracs in rv.get_piecewise_pdf().getDiracs()] for rv in self.info_state_rvs[1:]]
            info_state_comb = []
            info_state_comb_p = []
            for i in range(len(self.info_state_rvs) - 1):
                info_state_comb.append(list(sum(c) for c in itertools.product(*info_vals[i:])))
                info_state_comb_p.append(list(numpy.product(c) for c in itertools.product(*info_vals_p[i:])))

            info_states = list(itertools.product(*info_state_comb))
            info_states_p = list(numpy.product(ps) for ps in itertools.product(*info_state_comb_p))
            self.info_states_cache = info_states
            for info_state, p in zip(info_states, info_states_p):
                if info_state in self.info_states_prob_cache:
                    self.info_states_prob_cache[info_state] += p
                else:
                    self.info_states_prob_cache[info_state] = p
            return self.info_states_cache

    def get_info_state_prob(self, o):
        if self.info_states_prob_cache:
            return self.info_states_prob_cache[o]
        else:
            self.info_states()
            return self.info_states_prob_cache[o]

    # def lambda_t(self, o):
    #     return o[0] + self.info_state_rvs[-1]
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
    def lt_demand(self, lt_o):
        s = time.time()
        known_demand_rv = self.usage_model.usage(lt_o) \
            if lt_o else pacal.ConstDistr(0)

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
    def G_future(self, y, lt_o):
        x = y - self.lt_demand(lt_o)
        h_cost = self.h * pacal.max(x, 0).mean()
        b_cost = -self.b * pacal.min(x, 0).mean()
        cost = h_cost + b_cost
        v = self.gamma ** self.lead_time * cost

        self.g_b[(y, lt_o)] = self.gamma ** self.lead_time * b_cost
        self.g_h[(y, lt_o)] = self.gamma ** self.lead_time * h_cost
        return v

    def G_b(self, y, o):
        self.G(y, o)
        lt_o = sum(o[0:self.lead_time + 1])
        return self.g_b[(y, lt_o)]

    def G_h(self, y, o):
        self.G(y, o)
        lt_o = sum(o[0:self.lead_time + 1])
        return self.g_h[(y, lt_o)]

    def G_p(self, y, o):
        self.G(y, o)
        lt_o = sum(o[0:self.lead_time + 1])
        return self.g_p[(y, lt_o)]

    def G(self, y, o):
        lt_o = sum(o[0:self.lead_time + 1])
        if (y, lt_o) in self.reward_funcion_g_cache:
            return self.reward_funcion_g_cache[(y, lt_o)]

        self.reward_funcion_g_cache[(y, lt_o)] = (1 - self.gamma) * self.c * y + self.G_future(y, lt_o)
        self.g_p[(y, lt_o)] = (1 - self.gamma) * self.c * y
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

    def j_function_b(self, t, x, o):
        self.j_function(t, x, o)
        return 0 if t == -1 else self.j_b[(t, x, o)]

    def j_function_h(self, t, x, o):
        self.j_function(t, x, o)
        return 0 if t == -1 else self.j_h[(t, x, o)]

    def j_function_p(self, t, x, o):
        self.j_function(t, x, o)
        return 0 if t == -1 else self.j_p[(t, x, o)]

    def j_function_k(self, t, x, o):
        self.j_function(t, x, o)
        return 0 if t == -1 else self.j_k[(t, x, o)]

    def j_function(self, t, x, o):
        if (t, x, o) in self.value_function_j:
            return self.value_function_j[(t, x, o)]
        elif t == -1:
            return 0
        else:
            # Exploit S s structure
            stock_up_lvl, base_stock_lvl = self.stock_up_level(t, o), self.base_stock_level(t, o)
            y = stock_up_lvl if x <= base_stock_lvl else x
            k = self.k if x <= base_stock_lvl else 0
            j_value = k + self.v_function(t, y, o)

            self.value_function_j[(t, x, o)] = j_value
            if self.detailed:
                j_b = self.v_b[(t, y, o)]
                j_h = self.v_h[(t, y, o)]
                j_p = self.v_p[(t, y, o)]
                j_k = k + self.v_k[(t, y, o)]
                self.j_b[(t, x, o)] = j_b
                self.j_h[(t, x, o)] = j_h
                self.j_p[(t, x, o)] = j_p
                self.j_k[(t, x, o)] = j_k

            return j_value

    def compute_policies_parallel(self, t):
        policies = Pool(8).map(self.compute_policy, list((t, o) for o in self.info_states()))
        for policy, o in zip(policies, self.info_states_cache):
            order_up, reorder_pt = policy
            self.base_stock_level_cache[(t, o)] = reorder_pt
            self.value_function_v_argmin[(t, o)] = order_up

    def compute_j_value_parallel(self, t):
        max_x = max(self.value_function_v_argmin[(t, o)] for o in self.info_states()) + 10
        states = list((t, x, o) for x in range(max_x) for o in self.info_states())
        j_values = Pool(8).map(self.compute_j, states)
        self.value_function_j = dict()
        for j_value, state in zip(j_values, states):
            self.value_function_j[state] = j_value
        clear_states = list((t-1, x, o) for x in range(max_x) for o in self.info_states_cache)

    def compute_policy(self, args):
        t, o = args
        stock_up_level = self.v_function_argmin(t, o)
        v_min = self.v_function(t, stock_up_level, o)
        reorder_pt = stock_up_level
        while self.v_function(t, float(reorder_pt), o) < v_min + self.k:
            reorder_pt -= self.increments
        return stock_up_level, reorder_pt

    def compute_j(self, args):
        t, x, o = args
        return self.j_function(t, x, o)

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
        # MAYBE USE MULTIPROCESSING HERE TO SPEED UP A SINGLE MODEL.
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

        if self.detailed:
            self.v_b[(t, y, o)] = self.G_b(y, o) + self.gamma * sum(p * self.j_function_b(*state)
                                                                    for p, state in zip(probabilities, new_states))
            self.v_h[(t, y, o)] = self.G_h(y, o) + self.gamma * sum(p * self.j_function_h(*state)
                                                                    for p, state in zip(probabilities, new_states))
            self.v_p[(t, y, o)] = self.G_p(y, o) + self.gamma * sum(p * self.j_function_p(*state)
                                                                    for p, state in zip(probabilities, new_states))
            self.v_k[(t, y, o)] = self.gamma * sum(p * self.j_function_k(*state)
                                                   for p, state in zip(probabilities, new_states))
        self.value_function_v[(t, y, o)] = value
        return value

    def to_pickle(self, filename):
        with open(filename + "_model.pickle", "wb") as f:
            pickle.dump(self, f)


def get_model(config):
    model = StationaryOptModel(config.params["gamma"],
                               config.params["lead_time"],
                               config.params["info_state_rvs"],
                               config.params["holding_cost"],
                               config.params["backlogging_cost"],
                               config.params["setup_cost"],
                               config.params["unit_price"],
                               increments=config.params["increments"],
                               usage_model=config.params["usage_model"])
    return model


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
                                    'information_state_p',
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
                               usage_model=config.params["usage_model"],
                               detailed=config.params["detailed"])
    print("Starting {}: {}".format(config.sub_label, datetime.now().isoformat()))
    s = time.time()
    for t in ts:
        for x in xs:
            for o in model.info_states():
                info_p = model.get_info_state_prob(o)
                j_value = model.j_function(t, x, o)

                base_stock = model.base_stock_level(t, o)
                stock_up = model.stock_up_level(t, o)

                result = dict(config.params)
                if model.detailed:
                    j_k = model.j_function_k(t, x, o)
                    j_b = model.j_function_b(t, x, o)
                    j_h = model.j_function_h(t, x, o)
                    j_p = model.j_function_p(t, x, o)
                    result.update({'label': config.label,
                                   't': t,
                                   'inventory_position_state': x,
                                   'information_state': o,
                                   'information_state_p': info_p,
                                   'j_value_function': j_value,
                                   'j_k': j_k,
                                   'j_b': j_b,
                                   'j_h': j_h,
                                   'j_p': j_p,
                                   'base_stock': base_stock,
                                   'order_up_to': stock_up})
                else:
                    result.update({'label': config.label,
                                   't': t,
                                   'inventory_position_state': x,
                                   'information_state': o,
                                   'information_state_p': info_p,
                                   'j_value_function': j_value,
                                   'base_stock': base_stock,
                                   'order_up_to': stock_up})



                results = results.append(result, ignore_index=True)
        results.to_pickle(config.results_fn)
    duration = time.time() - s
    print("Finished {}: {} - {}".format(config.sub_label, datetime.now().isoformat(), str(duration)))
    if not os.path.exists("{}_{}".format(date.today().isoformat(), config.label)):
        os.mkdir("{}_{}".format(date.today().isoformat(), config.label))
    model.to_pickle("{}_{}/{}".format(date.today().isoformat(), config.label, config.sub_label))


def run_configs(configs, ts, xs, pools=4):
    print("Starting {} Runs: {}".format(str(len(configs)), datetime.now().isoformat()))
    Pool(pools).map(run_config, list((config, ts, xs) for config in configs))
    results = list(pd.read_pickle(config.results_fn) for config in configs)
    results = pd.concat(results)
    merged_fn = "{}_{}.pickle".format(date.today().isoformat(), configs[0].label)
    results.to_pickle(merged_fn)
    for config in configs:
        os.remove(config.results_fn)


if __name__ == "__main__":
    gamma = 0.9
    lead_time = 0
    horizon = 2
    info_state_rvs = [pacal.ConstDistr(0),
                      pacal.ConstDistr(0),
                      #pacal.DiscreteDistr([1, 2, 19, 20], [0.25, 0.25, 0.25, 0.25])
                      pacal.PoissonDistr(5, trunk_eps=1e-3) ]
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
                               info_state_rvs,
                               holding_cost,
                               backlogging_cost,
                               setup_cost,
                               unit_price,
                               usage_model=usage_model)

    # t, x, o = model.state_transition(10, 10, (3, 2))

    # s = time.time()
    # print(model.j_function(1, 0, (3, 2)))
    # print("run time:", time.time() - s)
    # s = time.time()
    # print(model.j_function(2, 0, (3, 2)))
    # print("run time:", time.time() - s)
    # s = time.time()
    # print(model.j_function(3, 0, (3, 2)))
    # print("run time:", time.time() - s)
    # s = time.time()
    # print(model.j_function(4, 0, (3, 2)))
    # print("run time:", time.time() - s)
    # s = time.time()
    # print(model.j_function(5, 0, (3, 2)))
    # print("run time:", time.time() - s)
    # s = time.time()

    s = time.time()
    model.compute_policies_parallel(0)
    model.compute_j_value_parallel(0)
    model.compute_policies_parallel(1)
    model.compute_j_value_parallel(1)
    model.compute_policies_parallel(2)
    model.compute_j_value_parallel(2)
    print("run time:", time.time() - s)
    print(model.value_function_j)
    max_x = max(key[1] for key in model.value_function_j.keys())
    print(max_x)

    model = StationaryOptModel(gamma,
                               lead_time,
                               info_state_rvs,
                               holding_cost,
                               backlogging_cost,
                               setup_cost,
                               unit_price,
                               usage_model=usage_model)
    s = time.time()
    for t in range(3):
        for o in model.info_states():
            for x in range(max_x+1):
                model.j_function(t, x, o)
    print("run time:", time.time() - s)
    print(model.value_function_j)


    # print(model.value_function_j)
    # print(model.value_function_v)
    # print(model.v_function(0, 3, (3, 2)))
    # print(model.v_function(0, 4, (3, 2)))
    # print(model.v_function(0, 5, (3, 2)))
    # print(model.v_function(0, 6, (3, 2)))
    # print(model.v_function(0, 7, (3, 2)))
    # print(model.v_function(0, 8, (3, 2)))
