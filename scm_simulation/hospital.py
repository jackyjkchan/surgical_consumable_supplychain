import pandas as pd
import numpy as np
import pickle


class SurgeryDemandProcess(object):
    """
    Base class for booking surgeries. Derives into elective and emergency booking classes.
    """
    def __init__(self, surgeries, rng, weekday_only=True):
        self.surgeries = surgeries
        self.rng = rng
        self.weekday_only = weekday_only

    def generate(self, start_day=0, days=1):
        start = start_day % 7
        weekends = set([(5 - start) % 7, (6 - start) % 7])
        num_surgeries = self.rng.gen_n(days)
        surgeries = list(list(np.random.choice(self.surgeries, num)) for num in num_surgeries)

        if self.weekday_only:
            for i in range(days):
                if i % 7 in weekends:
                    surgeries[i] = []
        return surgeries


class HistoricalElectiveSurgeryDemandProcess(SurgeryDemandProcess):
    def __init__(self):
        with open("scm_implementation/simulation_inputs/historical_elective_schedule.pickle", "rb") as f:
            elective_schedule = pickle.load(f)
        self.schedule = elective_schedule

    def generate(self, start_day=0, days=1):
        return self.schedule + [[]]*(days-len(self.schedule))


class HistoricalEmergencySurgeryDemandProcess(SurgeryDemandProcess):
    def __init__(self):
        with open("scm_implementation/simulation_inputs/historical_emergency_schedule.pickle", "rb") as f:
            emergency_schedule = pickle.load(f)
        self.schedule = emergency_schedule

    def generate(self, start_day=0, days=1):
        return self.schedule + [[]]*(days-len(self.schedule))


class ElectiveSurgeryDemandProcess(SurgeryDemandProcess):
    """
    Elective booking process.
    model_params (n=int, p=int): binomial n, p for weekdays [0,...,4], 0 for weekends [5, 6]
    """
    def __init__(self, surgeries, model_params, weekday_only=True):
        SurgeryDemandProcess.__init__(self, surgeries, model_params)
        assert len(model_params) == 2
        assert type(model_params[0]) == int
        assert type(model_params[1]) == float
        self.n = model_params[0]
        self.p = model_params[1]
        self.weekday_only = weekday_only

    def generate(self, start_day=0, days=1):
        start = start_day % 7
        weekends = set([(5-start)%7, (6-start)%7])
        num_surgeries = np.random.binomial(self.n, self.p, size=days)
        surgeries = list(list(np.random.choice(self.surgeries, num)) for num in num_surgeries)
        if self.weekday_only:
            for i in range(days):
                if i % 7 in weekends:
                    surgeries[i] = []
        return surgeries


class EmergencySurgeryDemandProcess(SurgeryDemandProcess):
    """
    Elective booking process.
    model_params (n=int, p=int): binomial n, p for weekdays [0,...,4], 0 for weekends [5, 6]
    """
    def __init__(self, surgeries, model_params):
        SurgeryDemandProcess.__init__(self, surgeries, model_params)
        self.mu = model_params

    def generate(self, start_day=0, days=1):
        num_surgeries = np.random.poisson(self.mu, size=days)
        surgeries = list(list(np.random.choice(self.surgeries, num)) for num in num_surgeries)
        return surgeries


class Hospital:
    """
    Hospital simulation object
    Backlog surgeries if not all items are available.
    """
    def __init__(self,
                 item_ids,
                 ordering_policies,
                 item_lead_times,
                 emergency_surgery_process,
                 elective_surgery_process,
                 sim_time=10000,
                 warm_up=100,
                 end_buffer=100):
        # hospital parameters, these are set at the start of the simulation and do not change
        #   item_ids to simulate
        #   surgeries to simulation
        #   ordering policy
        #   order lead time distribution

        # list of item ids [str, ...]
        self.item_ids = item_ids
        # list of surgery objects to simulate [scm_sim.Surgery, ...] this is not very useful. For validation mostly
        self.max_periods = sim_time + warm_up + end_buffer
        self.sim_time = sim_time
        self.warm_up = warm_up
        self.end_buffer = end_buffer

        # dictionaries
        # {item_id : policy_obj}
        self.ordering_policies = ordering_policies
        # {item_id: NumberGenerator}
        self.item_lead_time_generator = item_lead_times

        # objects for booking surgeries: SurgeryDemandProcess
        self.emergency_surgery_process = emergency_surgery_process
        self.elective_surgery_process = elective_surgery_process

        # Current state of the hospital
        #   clock
        #   inventory level {item_id: inventory_lvl}
        #   inventory position {item_id: inventory_position}
        #   surgery_backlog

        # current initial inventory level for each item
        self.clock = 0
        self.curr_inventory_lvl = {item_id: 0 for item_id in item_ids}
        self.curr_inventory_position = {item_id: 0 for item_id in item_ids}
        self.curr_surgery_backlog = []

        # Full historical states
        # all item deliveries, inventory_level, surgery_backlog, order_qty
        self.full_item_deliveries = {item_id: self.max_periods*[0] for item_id in item_ids}
        self.full_inventory_lvl = {item_id: self.max_periods * [0] for item_id in item_ids}
        self.full_order_qty = {item_id: self.max_periods * [0] for item_id in item_ids}
        self.full_item_demand = {item_id: self.max_periods * [0] for item_id in item_ids}
        self.full_surgery_backlog = self.max_periods * [None]

        self.full_elective_schedule = self.elective_surgery_process.generate(days=self.max_periods)
        self.full_emergency_schedule = self.emergency_surgery_process.generate(days=self.max_periods)
        self.full_item_info_state = {item_id: self.max_periods * [0] for item_id in item_ids}

    def process_orders(self):
        for item_id in self.ordering_policies:
            action = self.ordering_policies[item_id].action(self)
            self.curr_inventory_position[item_id] += action
            lt = self.item_lead_time_generator[item_id].gen()
            self.full_item_deliveries[item_id][self.clock + lt] = action
            self.full_order_qty[item_id][self.clock] = action

    def process_deliveries(self):
        for item_id in self.ordering_policies:
            qty = self.full_item_deliveries[item_id][self.clock]
            self.curr_inventory_lvl[item_id] += qty

    def process_demand(self):
        all_surgeries = self.full_elective_schedule[self.clock] + \
                        self.full_emergency_schedule[self.clock] + \
                        self.curr_surgery_backlog
        next_surgery_backlog = []
        for surgery in all_surgeries:
            item_demand = {iid: surgery.item_usages[iid].gen() for iid in surgery.item_usages}
            if all(self.curr_inventory_lvl[item_id] >= item_demand[item_id] for item_id in self.item_ids):
                for item_id in self.item_ids:
                    self.curr_inventory_lvl[item_id] -= item_demand[item_id]
                    self.curr_inventory_position[item_id] -= item_demand[item_id]
                    self.full_item_demand[item_id][self.clock] += item_demand[item_id]
            else:
                next_surgery_backlog.append(surgery)
        self.curr_surgery_backlog = next_surgery_backlog

    def advance_clock(self):
        for iid in self.item_ids:
            self.full_inventory_lvl[iid][self.clock] = self.curr_inventory_lvl[iid]
        self.full_surgery_backlog[self.clock] = self.curr_surgery_backlog
        self.clock += 1

    def trim_data(self):
        s = self.warm_up
        e = self.max_periods - self.end_buffer
        self.full_inventory_lvl = {iid: self.full_inventory_lvl[iid][s:e] for iid in self.full_inventory_lvl}
        self.full_surgery_backlog = self.full_surgery_backlog[s:e]
        self.full_emergency_schedule = self.full_emergency_schedule[s:e]
        self.full_elective_schedule = self.full_elective_schedule[s:e]
        self.full_item_deliveries = {iid: self.full_item_deliveries[iid][s:e] for iid in self.full_item_deliveries}
        self.full_order_qty = {iid: self.full_order_qty[iid][s:e] for iid in self.full_order_qty}
        self.full_item_demand = {iid: self.full_item_demand[iid][s:e] for iid in self.full_item_demand}

    def run_simulation(self):
        while self.clock < self.max_periods - self.end_buffer:
            self.process_orders()
            self.process_deliveries()
            self.process_demand()
            self.advance_clock()

    def to_pickle(self, fn):
        with open(fn + ".pickle", "wb") as f:
            pickle.dump(self, f)
