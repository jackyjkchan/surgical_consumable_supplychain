import simpy
from scm_simulation.rng_classes import GenerateDeterministic, GenerateFromSample
from scm_simulation.simulation_processes import *
from scm_simulation.order_policies import *
from scm_simulation.hospital import Hospital
import random
from pprint import pprint

RANDOM_SEED = 0
SIM_TIME = 30


def main():
    item_ids = ["item1"]

    ordering_policies = {
        "item1": DeterministicConDOIPolicy("item1", constant_days=4)
    }

    item_delivery_times = {
        "item1": GenerateDeterministic(3)
    }

    initial_inventory = {
        "item1": 24
    }

    outstanding_orders = {
        "item1": set()
    }

    item_stochastic_demands = {
        "item1": GenerateDeterministic(3)
    }

    random.seed(RANDOM_SEED)
    hospital = Hospital(item_ids,
                        ordering_policies,
                        item_delivery_times,
                        item_stochastic_demands,
                        initial_inventory,
                        outstanding_orders)

    env = simpy.Environment()

    env.process(place_order(env, ordering_policies, item_delivery_times, hospital))
    env.process(demand_stochastic(env, item_stochastic_demands, hospital))
    env.process(hospital_bookkeeping(env, hospital))
    env.run(until=SIM_TIME)
    print("historical inventory levels")
    print(hospital.historical_inventory_levels)
    print("Item stock out events")
    pprint(hospital.stockouts)
    print("order history")
    print(hospital.historical_orders)


if __name__ == "__main__":
    main()
