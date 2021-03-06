from scm_optimization.model import *
from scipy.optimize import minimize, bisect, minimize_scalar
from functools import lru_cache


class DualBalancing:
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

        no_info_booking = sum(self.info_state_rvs)
        no_info_demand_pdf = sum([dirac.f * self.usage_model.usage(dirac.a).get_piecewise_pdf()
                                  for dirac in no_info_booking.get_piecewise_pdf().getDiracs()
                                  ])
        self.no_info_demand = pacal.DiscreteDistr([dirac.a for dirac in no_info_demand_pdf.getDiracs()],
                                                  [dirac.f for dirac in no_info_demand_pdf.getDiracs()])
        self.unknown_demand_cache = []
        prev = 0
        for i in range(0, len(self.info_state_rvs)):
            booking_rv = sum(self.info_state_rvs[0:i + 1])
            demand_pdf = sum([dirac.f * self.usage_model.usage(dirac.a).get_piecewise_pdf()
                              for dirac in booking_rv.get_piecewise_pdf().getDiracs()
                              ])
            demand_rv = pacal.DiscreteDistr([dirac.a for dirac in demand_pdf.getDiracs()],
                                            [dirac.f for dirac in demand_pdf.getDiracs()])
            demand_rv += prev
            self.unknown_demand_cache.append(demand_rv)
            prev = demand_rv
        self.demand_rv_cache = {}  # (periods, o) -> RV
        self.q_cache = {}

    def trunk_rv(self, rv, trunk=1e-4):
        a = [dirac.a for dirac in rv.get_piecewise_pdf().getDiracs()]
        f = [dirac.f for dirac in rv.get_piecewise_pdf().getDiracs()]
        head = 0
        tail = 0
        while head < trunk / 2 and f[0] < trunk / 2:
            head += f[0]
            a.pop(0)
            f.pop(0)
        while tail < trunk and f[-1] < trunk:
            tail += f[-1]
            a.pop(-1)
            f.pop(-1)
        rv = pacal.DiscreteDistr([aa for aa in a],
                                 [ff/(1-head-tail) for ff in f])
        return rv

    def window_demand(self, t, j, o):
        print("in window_demand", t, j, o)
        """
        :param t: current period, dummy variable for stationary case
        :param j: end period (inclusive) 0 is the last period.
        :param o: info state
        :return: demand rv, cumulative demand RV for periods t to j given information o
        """
        periods = t - j + 1
        cumul_o = sum(o[0:min(len(o), periods)])
        if (periods, cumul_o) in self.demand_rv_cache:
            return self.demand_rv_cache[(periods, cumul_o)]

        while len(self.unknown_demand_cache) < periods:
            rv = self.unknown_demand_cache[-1] + self.no_info_demand
            rv = pacal.DiscreteDistr([dirac.a for dirac in rv.get_piecewise_pdf().getDiracs()],
                                     [dirac.f for dirac in rv.get_piecewise_pdf().getDiracs()])
            rv = self.trunk_rv(rv)
            self.unknown_demand_cache.append(rv)
        index = periods - 1
        rv = self.usage_model.usage(cumul_o) + self.unknown_demand_cache[index]
        rv = pacal.DiscreteDistr([dirac.a for dirac in rv.get_piecewise_pdf().getDiracs()],
                                 [dirac.f for dirac in rv.get_piecewise_pdf().getDiracs()])

        self.demand_rv_cache[(periods, cumul_o)] = rv
        return self.demand_rv_cache[(periods, cumul_o)]

    def h_db(self, q, t, x, o):
        print(" in h_db", q, t, x, o)
        """"Expected holding cost incurred by order size of q by those units from t to end of horizon
            state space is t for current priod
            o for info state
            x for current inventory position
        """
        expected_cost = 0
        s = t - self.lead_time
        while s >= 0:
            over_stock = pacal.max(0,
                                   q - pacal.max(0,
                                                 self.window_demand(t, s, o) - pacal.ConstDistr(x)
                                                 )
                                   )
            diff = over_stock.mean() * self.h
            if diff < self.usage_model.trunk:
                #print(t, s)
                break
            expected_cost += over_stock.mean() * self.h
            s -= 1
        return expected_cost

    def pi_db(self, q, t, x, o):
        s = t - self.lead_time
        under_stock = pacal.max(0, self.window_demand(t, s, o) - x - q)
        expected_cost = under_stock.mean() * self.b
        return expected_cost

    def la_objective(self, q, t, x, o):
        return self.h_db(q, t, x, o) + self.pi_db(q, t, x, o)

    def order_la(self, t, x, o):
        print(t, x, o)
        prev, cost = float('inf'), float('inf')
        for q in range(0, 50):
            cost = self.la_objective(q, t, x, o)
            if cost < prev:
                prev = cost
            else:
                return q-1
        print("MAXIMUM HIT: ERROR")
        return q

    # @lru_cache()
    def g_objective(self, q, t, x, o):
        #print("in g_objective")
        return max([self.h_db(q, t, x, o),
                    self.pi_db(q, t, x, o)])

    # @lru_cache()
    def order_q_continuous(self, t, x, o):
        print(t, x, o)
        if (t, x, 0) in self.q_cache:
            return self.q_cache[(x, t, o)]

        q = minimize_scalar(lambda qq: self.g_objective(qq, t, x, o),
                               bracket=[0, 50],
                               bounds=[0, 50],
                               method='Bounded',
                               options={'xatol': 1e-03, 'maxiter': 500, 'disp': 0}).x
        self.q_cache[(x, t, o)] = q
        return q

    # @staticmethod
    # def abs_rv(rv):
    #     rv.get()

    def info_states(self):
        if len(self.info_state_rvs) == 1:
            pass
        if self.info_states_cache:
            return self.info_states_cache
        else:
            info_vals = [[diracs.a for diracs in rv.get_piecewise_pdf().getDiracs()] for rv in self.info_state_rvs[1:]]
            info_vals_p = [[diracs.f for diracs in rv.get_piecewise_pdf().getDiracs()] for rv in
                           self.info_state_rvs[1:]]
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

    # # Cumulative demand RV for time periods t to up to but excluding j. Note j = -1 means cumulative demand for periods
    # # t till end of planning horizon
    # def window_demand(self, t, j, o):
    #     demand_rv = 0
    #     for i in range(t, j, -1):
    #         demand_rv += self.unknown_lt_demand_rv
    #         if i < len(o):
    #             demand_rv += self.usage_model.usage(0[i])
    #         else:
    #             demand_rv += self.

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


if __name__ == "__main__":
    gamma = 1
    lead_time = 0
    #horizon = 0
    info_state_rvs = [pacal.ConstDistr(0),
                      pacal.ConstDistr(0),
                      pacal.BinomialDistr(10, 0.5)]
    info_state_rvs = [pacal.BinomialDistr(10, 0.5)]
    holding_cost = 1
    backlogging_cost = 10
    setup_cost = 0
    unit_price = 0
    usage_model = PoissonUsageModel(scale=1)
    # usage_model = lambda o: pacal.ConstDistr(o)
    # usage_model = lambda o: pacal.PoissonDistr(o, trunk_eps=1e-3)
    # sage_model = None
    model = DualBalancing(gamma,
                          lead_time,
                          info_state_rvs,
                          holding_cost,
                          backlogging_cost,
                          setup_cost,
                          unit_price,
                          usage_model=usage_model)

    s = time.time()
    for t in range(20):
        for o in model.info_states()[-1:]:
            o = (5, 4)
            o=tuple()
            for x in range(1):
                q = model.order_q_continuous(t, x, o)
                hc = model.h_db(q, t, x, o)
                bc = model.pi_db(q, t, x, o)
                print("t: {}; o: {}, x: {}".format(t, o, x))
                print("\t q: {}, hc: {}, bc: {}".format(q, hc, bc))

    print("run time:", time.time() - s)
