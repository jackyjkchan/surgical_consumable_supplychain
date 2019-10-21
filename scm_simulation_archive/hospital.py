import numpy as np

class Hospital:

    def __init__(self, item_ids, ordering_policies, item_delivery_times, item_stochastic_demands, initial_inventory,
                 outstanding_orders, surgeries=[]):
        # hospital parameters, these are set at the start of the simulation and do not change
        #   item_ids to simulate
        #   ordering policy
        #   order lead time distribution
        #   stochastic demand distribution

        # list of item ids and surgery labels to simulate
        self.item_ids = item_ids
        self.surgeries = surgeries
        # dictionaries
        # item_id : policy_obj
        self.ordering_policies = ordering_policies
        # item_id: NumberGenerator
        self.order_lead_times = item_delivery_times

        # Demand side
        # item_id: NumberGenerator, random demand for items (no surgeries)
        self.item_stochastic_demands = item_stochastic_demands

        # {surgery_label: {item_id: NumberGenerator}}
        # lookup table for item usage object by surgery label
        self.surgery_item_usage = None

        # surgery_label: NumberGenerator
        # random demand for unbooked surgeries
        self.surgery_stochastic_demand = None

        # surgery_label: NumberGenerator
        # random demand for booked surgeries
        self.booked_surgery_stochastic_demand = None

        # State variables of the hospital
        #   inventory, stock of items
        #   outstanding orders

        # current initial inventory level for each item
        self.inventory = initial_inventory
        assert (item_id in initial_inventory for item_id in item_ids)

        # outstanding orders
        self.orders = outstanding_orders if outstanding_orders else {item_id: set() for item_id in item_ids}

        # keep track of number of surgeries being booked into the schedule.
        # dictionary mapping surgery label to list. surgery_schedule["A"][x] = number of surgery A booked for day x.
        self.surgery_schedule = {surgery: [0] for surgery in surgeries}

        # Performance measures to collect
        #   stock out events

        # dict storing list of times of stockout events per item
        self.stockouts = {item_id: [] for item_id in item_ids}
        self.historical_inventory_levels = {item_id: [initial_inventory[item_id]] for item_id in item_ids}
        self.historical_orders = {item_id: [] for item_id in item_ids}
        self.historical_deliveries = {item_id: [] for item_id in item_ids}
        self.historical_demand = {item_id: [] for item_id in item_ids}

    def set_surgery_item_usage(self, surgery_item_usage):
        self.surgery_item_usage = surgery_item_usage

    def set_order_lead_times(self, order_lead_times):
        self.order_lead_times = order_lead_times

    def set_surgery_stochastic_demand(self, surgery_stochastic_demand):
        self.surgery_stochastic_demand = surgery_stochastic_demand

    def set_booked_surgery_stochastic_demand(self, booked_surgery_stochastic_demand):
        self.booked_surgery_stochastic_demand = booked_surgery_stochastic_demand

    def set_policy(self, policy):
        self.ordering_policies = policy

    def set_sim_time(self, sim_time):
        self.historical_inventory_levels = {item_id: [0] * sim_time for item_id in self.item_ids}
        self.historical_orders = {item_id: [0] * sim_time for item_id in self.item_ids}
        self.historical_deliveries = {item_id: [0] * sim_time for item_id in self.item_ids}
        self.historical_demand = {item_id: [0] * sim_time for item_id in self.item_ids}
        self.surgery_schedule = {surgery: [0] * sim_time for surgery in self.surgeries}

    def clean_data(self, warm_up):
        for item_id in self.item_ids:
            self.historical_inventory_levels[item_id] = self.historical_inventory_levels[item_id][warm_up:]
            self.historical_orders[item_id] = self.historical_orders[item_id][warm_up:]
            self.historical_deliveries[item_id] = self.historical_deliveries[item_id][warm_up:]
            self.historical_demand[item_id] = self.historical_demand[item_id][warm_up:]
            self.stockouts[item_id] = [t-warm_up for t in self.stockouts[item_id]]
            self.stockouts[item_id] = list(filter(lambda x: x >= 0, self.stockouts[item_id]))


class HospitalPreGenerated(Hospital):
    def __init__(self, item_ids,
                 ordering_policies,
                 item_delivery_times,
                 item_stochastic_demands,
                 initial_inventory,
                 outstanding_orders,
                 surgeries):

        Hospital.__init__(self,
                          item_ids,
                          ordering_policies,
                          item_delivery_times,
                          item_stochastic_demands,
                          initial_inventory,
                          outstanding_orders,
                          surgeries)

        self.sum_surgery = {}
        self.new_booked_surgery_stochastic_demand = {}
        self.historical_stochastic_item_demands = {}
        self.all_lead_times = {}
        self.new_surgery_item_usage = {}
        self.new_surgery_stochastic_demand = {}
        self.elective_surgery_schedule = {}
        self.emergency_surgery_schedule = {}

    def setrandomvars(self, sim_time, seed=0):
        np.random.seed(seed)

        self.all_lead_times = {item: [self.order_lead_times[item].gen()
                                      for _ in range(sim_time)] for item in self.item_ids}

        self.emergency_surgery_schedule = {
            surgery: [self.surgery_stochastic_demand[surgery].gen() for _ in range(sim_time)]
            for surgery in self.surgeries
        }

        self.elective_surgery_schedule = {
            surgery: list(self.booked_surgery_stochastic_demand[surgery].gen() for _ in range(sim_time))
            for surgery in self.surgeries
        }
        self.surgery_schedule = self.elective_surgery_schedule

        self.historical_stochastic_item_demands = {
            item: [self.item_stochastic_demands[item].gen() for _ in range(sim_time)] for item in self.item_ids
        }

        total_surgeries = {
            surgery: [
                (int(self.elective_surgery_schedule[surgery][i])+int(self.emergency_surgery_schedule[surgery][i]))
                      for i in range(sim_time)
            ] for surgery in self.surgeries
        }

        self.historical_demand = {
            item: list(
                sum(sum(self.surgery_item_usage[surgery][item].gen_n(total_surgeries[surgery][i]))
                    for surgery in self.surgeries)
                for i in range(sim_time)
            ) for item in self.item_ids
        }

        for item in self.item_ids:
            for i in range(sim_time):
                self.historical_demand[item][i] += self.historical_stochastic_item_demands[item][i]

        return
