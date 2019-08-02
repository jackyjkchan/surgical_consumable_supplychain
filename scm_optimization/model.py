import math
import pacal
from collections import defaultdict
import itertools
import numpy
import time


class StationaryOptModel:
    def __init__(self, gamma, lead_time, horizon, info_state_rvs,
                 holding_cost, backlogging_cost, setup_cost, unit_price,
                 max_info_state=None, info_steps=None):

        # parameters in order:
        # single period discount factor
        # lead time for items to arrive, >= 0
        # information horizon N >= 0, N = 0 for no advanced information
        # vector of random variables, transition of the state of advanced information, M_{t, s} in notation

        self.gamma = gamma
        self.lead_time = lead_time
        self.horizon = horizon
        self.info_state_rvs = info_state_rvs

        self.h = holding_cost
        self.b = backlogging_cost
        self.k = setup_cost
        self.c = unit_price

        # static list of possible info states
        # self.info_states = list(range(max_info_state+info_steps))

        self.value_function_j = {}
        self.value_function_v = {}
        self.value_function_v_argmin = {}
        self.base_stock_level_cache = {}

        unknown_lt_info = sum(self.info_state_rvs[i] for j in range(self.lead_time + 1) for i in range(j + 1))
        if len(unknown_lt_info.get_piecewise_pdf().getDiracs()) == 1:
            unknown_lt_info = unknown_lt_info.get_piecewise_pdf().getDiracs()[0].a
            if unknown_lt_info:
                self.unknown_lt_demand_rv = pacal.PoissonDistr(unknown_lt_info, trunk_eps=1e-3)
            else:
                self.unknown_lt_demand_rv = 0
        else:
            unknown_lt_demand_pdf = sum([dirac.f * pacal.PoissonDistr(dirac.a, trunk_eps=1e-3).get_piecewise_pdf()
                                        for dirac in unknown_lt_info.get_piecewise_pdf().getDiracs()
                                        ])
            self.unknown_lt_demand_rv = pacal.DiscreteDistr([dirac.a for dirac in unknown_lt_demand_pdf.getDiracs()],
                                                            [dirac.f for dirac in unknown_lt_demand_pdf.getDiracs()])

        if len(self.info_state_rvs[0].get_piecewise_pdf().getDiracs()) == 1:
            val = self.info_state_rvs[0].get_piecewise_pdf().getDiracs()[0].a
            if val:
                self.unknown_demand_rv = pacal.PoissonDistr(unknown_lt_info, trunk_eps=1e-3)
            else:
                self.unknown_demand_rv = 0
        else:
            unknown_demand_pdf = sum([dirac.f * pacal.PoissonDistr(dirac.a, trunk_eps=1e-3).get_piecewise_pdf()
                                     for dirac in unknown_lt_info.get_piecewise_pdf().getDiracs()
                                     ])
            self.unknown_demand_rv = pacal.DiscreteDistr([dirac.a for dirac in unknown_demand_pdf.getDiracs()],
                                                         [dirac.f for dirac in unknown_demand_pdf.getDiracs()])


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
        known_demand_rv = pacal.PoissonDistr(sum(o[0:self.lead_time + 1]), trunk_eps=1e-3) \
            if sum(o[0:self.lead_time + 1]) else pacal.ConstDistr(0)

        # u_lead_time = sum(self.info_state_rvs[i] for j in range(self.lead_time+1) for i in range(j+1))
        # lambda_lead_time = u_lead_time + sum(o[0:self.lead_time + 1])
        # demand_pdf = sum([dirac.f * pacal.PoissonDistr(dirac.a).get_piecewise_pdf()
        #                   for dirac in lambda_lead_time.get_piecewise_pdf().getDiracs()
        #                   ])
        # demand_rv = pacal.DiscreteDistr([dirac.a for dirac in demand_pdf.getDiracs()],
        #                                 [dirac.f for dirac in demand_pdf.getDiracs()])
        lt_demand_rv = known_demand_rv
        if self.unknown_lt_demand_rv:
            lt_demand_rv += self.unknown_lt_demand_rv
        return lt_demand_rv

    # D_t | \Lambda_t in notation
    def current_demand(self, o):
        return pacal.PoissonDistr(o[0], trunk_eps=1e-3) \
               + self.unknown_demand_rv

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
        return (1 - self.gamma) * self.c * y + self.G_future(y, o)

    # state t is reversed, terminal stage is t=0 and starting stage is t=T
    # returns new state as random variables
    def state_transition(self, t, y, o):
        next_x = y - self.current_demand(o)
        for i, j in zip(self.info_state_rvs[1:], o[1:] + (0,)):
            z = i + j
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
            # y = self.v_function_argmin(t, o)
            # j_value = min(self.k + self.v_function(t, y, o), self.v_function(t, x, o)) \
            #     if y > x else self.v_function(t, x, o)
            # self.value_function_j[(t, x, o)] = j_value

            # Exploit S s structure
            stock_up_lvl = self.stock_up_level(t, o)
            base_stock_lvl = self.base_stock_level(t, o)
            if x <= base_stock_lvl:
                j_value = self.k + self.v_function(t, stock_up_lvl, o)
            else:
                j_value = self.v_function(t, x, o)
            self.value_function_j[(t, x, o)] = j_value
            return j_value

    def base_stock_level(self, t, o):
        if (t, o) in self.base_stock_level_cache:
            return self.base_stock_level_cache[(t, o)]
        else:
            stock_up_level = self.stock_up_level(t, o)
            x = stock_up_level

            # while do nothing at inv pos x is better than do something, go to lower inv pos.
            while self.v_function(t, x, o) < self.v_function(t, stock_up_level, o) + self.k:
                x -= 1
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
        y = 1
        while self.v_function(t, y, o) <= v_min + self.k:
            v = self.v_function(t, y, o)
            if v < v_min:
                y_min = y
                v_min = v
            y += 1

        self.value_function_v_argmin[(t, o)] = y_min
        return y_min

    def v_function(self, t, y, o):
        if (t, y, o) in self.value_function_v:
            return self.value_function_v[(t, y, o)]

        next_t, next_x, next_o = self.state_transition(t, y, o)

        new_states, probabilities = self.unpack_state_transition(next_t, next_x, next_o)
        start = time.time()

        value = self.G(y, o) + self.gamma * sum(p * self.j_function(*state)
                                                for p, state in zip(probabilities, new_states)
                                                )
        end = time.time()
        #print(end - start)
        self.value_function_v[(t, y, o)] = value
        return value


if __name__ == "__main__":
    gamma = 0.9
    lead_time = 0
    horizon = 2
    info_state_rvs = [pacal.ConstDistr(0),
                      pacal.ConstDistr(0),
                      pacal.DiscreteDistr([1, 2, 3, 4], [0.25, 0.25, 0.25, 0.25])]
    holding_cost = 1
    backlogging_cost = 10
    setup_cost = 5
    unit_price = 0

    model = StationaryOptModel(gamma,
                               lead_time,
                               horizon,
                               info_state_rvs,
                               holding_cost,
                               backlogging_cost,
                               setup_cost,
                               unit_price)

    #t, x, o = model.state_transition(10, 10, (3, 2))

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


    #print(model.value_function_j)
    #print(model.value_function_v)
    # print(model.v_function(0, 3, (3, 2)))
    # print(model.v_function(0, 4, (3, 2)))
    # print(model.v_function(0, 5, (3, 2)))
    # print(model.v_function(0, 6, (3, 2)))
    # print(model.v_function(0, 7, (3, 2)))
    # print(model.v_function(0, 8, (3, 2)))

