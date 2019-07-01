import simpy
from scm_simulation.rng_classes import GenerateDeterministic, GenerateFromSample
from scm_simulation.simulation_processes import *
from scm_simulation.order_policies import *
from scm_simulation.hospital import Hospital, HospitalPreGenerated
import random
from pprint import pprint
from collections import namedtuple
import numpy as np

RANDOM_SEED = 0
SIM_TIME = 30

item_sim_config_fields = ["item_ids",
                          "ordering_policies",
                          "item_delivery_times",
                          "initial_inventory",
                          "outstanding_orders",
                          "item_stochastic_demands"]

Item_Sim_Config = namedtuple('Item_Sim_Config', item_sim_config_fields)

stochastic_surgery_sim_config_fields = ["item_ids",
                                        "surgeries",
                                        "ordering_policies",
                                        "item_delivery_times",
                                        "initial_inventory",
                                        "outstanding_orders",
                                        "surgery_item_usage",
                                        "surgery_stochastic_demand",
                                        "item_stochastic_demands"]

Stochastic_Surgery_Config = namedtuple('Stochastic_Surgery_Config', stochastic_surgery_sim_config_fields)

booked_surgery_sim_config_fields = ["item_ids",
                                        "surgeries",
                                        "ordering_policies",
                                        "item_delivery_times",
                                        "initial_inventory",
                                        "outstanding_orders",
                                        "surgery_item_usage",
                                        "surgery_stochastic_demand",
                                        "surgery_booked_demand",
                                        "item_stochastic_demands"]

Booked_Surgery_Config = namedtuple('Booked_Surgery_Config', booked_surgery_sim_config_fields)


def run_pre_generated_hospital(hospital, sim_time=10500, warm_up=500):
    for i in range(0, sim_time):
        for item in hospital.item_ids:
            # Receive order
            hospital.inventory[item] += hospital.historical_deliveries[item][i]
            # Item demand from surgeries
            if hospital.inventory[item] < hospital.historical_demand[item][i]:
                hospital.inventory[item] = 0
                hospital.stockouts[item].append(i)
            else:
                hospital.inventory[item] -= hospital.historical_demand[item][i]
            # Place order
            order_qty = hospital.ordering_policies[item].action(i, hospital)
            hospital.historical_orders[item][i] += order_qty
            lead_time = hospital.all_lead_times[item][i]
            if i + lead_time < sim_time:
                hospital.historical_deliveries[item][i + lead_time] += order_qty
            # Hospital bookkeeping
            hospital.historical_inventory_levels[item][i] += hospital.inventory[item]
    hospital.clean_data(warm_up)
    return hospital


def run_pre_generated_rv_sim(config, simtime=10000, warmup=500, show=False):
    random.seed(RANDOM_SEED)
    hospital = HospitalPreGenerated(config.item_ids,
                                    config.ordering_policies,
                                    config.item_delivery_times,
                                    config.item_stochastic_demands,
                                    config.initial_inventory,
                                    config.outstanding_orders,
                                    config.surgeries)
    hospital.set_surgery_item_usage(config.surgery_item_usage)
    hospital.set_surgery_stochastic_demand(config.surgery_stochastic_demand)
    hospital.set_booked_surgery_stochastic_demand(config.surgery_booked_demand)
    hospital.set_sim_time(simtime)
    hospital.setrandomvars(simtime)
    for i in range(0, simtime):
        for item in hospital.item_ids:
            # Receive order
            hospital.inventory[item] += hospital.historical_deliveries[item][i]
            # Item demand from surgeries
            if hospital.inventory[item] < hospital.historical_demand[item][i]:
                hospital.inventory[item] = 0
                hospital.stockouts[item].append(i)
            else:
                hospital.inventory[item] -= hospital.historical_demand[item][i]

            # Place order
            order_qty = config.ordering_policies[item].action(i, hospital)
            hospital.historical_orders[item][i] += order_qty
            lead_time = hospital.all_lead_times[item][i]
            if i + lead_time < simtime:
                hospital.historical_deliveries[item][i + lead_time] += order_qty
            # Hospital bookkeeping
            hospital.historical_inventory_levels[item][i] += hospital.inventory[item]
    hospital.clean_data(warmup)
    if show:
        print("Average Inventory Level")
        for item_id in config.item_ids:
            print("{0}: {1}".format(item_id, str(np.mean(hospital.historical_inventory_levels[item_id]))))
        for item in hospital.stockouts:
            print("{0}: {1}".format(item, len(hospital.stockouts[item])))
        print(hospital.stockouts)
    return hospital


def run_item_driven_simulation(config, SIM_TIME=10000, WARMUP=500, show=False):
    item_ids = config.item_ids
    ordering_policies = config.ordering_policies
    item_delivery_times = config.item_delivery_times
    initial_inventory = config.initial_inventory
    outstanding_orders = config.outstanding_orders
    item_stochastic_demands = config.item_stochastic_demands

    random.seed(RANDOM_SEED)
    hospital = Hospital(item_ids,
                        ordering_policies,
                        item_delivery_times,
                        item_stochastic_demands,
                        initial_inventory,
                        outstanding_orders
                        )

    env = simpy.Environment()
    env.process(receive_order(env, hospital))
    env.process(item_demand(env, item_stochastic_demands, hospital))
    env.process(place_order(env, ordering_policies, item_delivery_times, hospital))
    env.process(hospital_bookkeeping(env, hospital))
    env.run(until=SIM_TIME)
    if show:
        print("Average Inventory Level")
        for item_id in item_ids:
            print("{0}: {1}".format(item_id, str(np.mean(hospital.historical_inventory_levels[item_id]))))

    return hospital


def run_stochastic_surgery_driven_simulation(config, SIM_TIME=100000, WARMUP=500, show=False):
    item_ids = config.item_ids
    ordering_policies = config.ordering_policies
    item_delivery_times = config.item_delivery_times
    initial_inventory = config.initial_inventory
    outstanding_orders = config.outstanding_orders

    random.seed(RANDOM_SEED)
    hospital = Hospital(item_ids,
                        ordering_policies,
                        item_delivery_times,
                        {},
                        initial_inventory,
                        outstanding_orders,
                        surgeries=config.surgeries)
    hospital.set_surgery_item_usage(config.surgery_item_usage)
    hospital.set_surgery_stochastic_demand(config.surgery_stochastic_demand)
    hospital.set_sim_time(SIM_TIME)
    env = simpy.Environment()
    env.process(receive_order(env, hospital))
    env.process(item_demand_from_surgeries(env, hospital))
    env.process(place_order(env, ordering_policies, item_delivery_times, hospital))
    env.process(hospital_bookkeeping(env, hospital))
    env.run(until=SIM_TIME)
    hospital.clean_data(WARMUP)
    if show:
        print("Average Inventory Level")
        for item_id in item_ids:
            print("{0}: {1}".format(item_id, str(np.mean(hospital.historical_inventory_levels[item_id]))))
        for item in hospital.stockouts:
            print("{0}: {1}".format(item, len(hospital.stockouts[item])))
        print(hospital.stockouts)
    return hospital


def run_booked_surgery_driven_simulation(config, SIM_TIME=100000, WARMUP=500, show=False):
    item_ids = config.item_ids
    ordering_policies = config.ordering_policies
    item_delivery_times = config.item_delivery_times
    initial_inventory = config.initial_inventory
    outstanding_orders = config.outstanding_orders

    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    hospital = Hospital(item_ids,
                        ordering_policies,
                        item_delivery_times,
                        {},
                        initial_inventory,
                        outstanding_orders,
                        surgeries=config.surgeries)
    hospital.set_surgery_item_usage(config.surgery_item_usage)
    hospital.set_surgery_stochastic_demand(config.surgery_stochastic_demand)
    hospital.set_booked_surgery_stochastic_demand(config.surgery_booked_demand)
    hospital.set_sim_time(SIM_TIME)
    env.process(receive_order(env, hospital))
    env.process(item_demand_from_surgeries(env, hospital))
    env.process(book_surgeries(env, hospital))
    env.process(place_order(env, ordering_policies, item_delivery_times, hospital))
    env.process(hospital_bookkeeping(env, hospital))
    env.run(until=SIM_TIME)
    hospital.clean_data(WARMUP)
    if show:
        print("Average Inventory Level")
        for item_id in item_ids:
            print("{0}: {1}".format(item_id, str(np.mean(hospital.historical_inventory_levels[item_id]))))
        for item in hospital.stockouts:
            print("{0}: {1}".format(item, len(hospital.stockouts[item])))
        print(hospital.stockouts)
    return hospital


if __name__ == "__main__":

    if False:
        """ Item Driven Simulation test"""
        for k in [5, 10, 15]:
            for l in [2, 3, 4]:
                condoi_level = k
                lead_time = l
                demand = 1
                config = Item_Sim_Config(
                    item_ids=["item1"],
                    ordering_policies={"item1": DeterministicConDOIPolicyV2("item1", constant_days=condoi_level)},
                    item_delivery_times={"item1": GenerateDeterministic(lead_time)},
                    initial_inventory={"item1": 0},
                    outstanding_orders={"item1": set()},
                    item_stochastic_demands={"item1": GenerateDeterministic(demand)}
                )
                print("=================== START REPORT===================")
                print("conDOI Level:", condoi_level)
                print("lead time:", lead_time)
                print("demand:", demand)
                run_item_driven_simulation(config, show=True)
                print("======================== END ========================")


    if False:
        """ Stochastic Surgery Driven Simulation test"""
        condoi_level = 5
        lead_time = 2
        config = Stochastic_Surgery_Config(
            item_ids=["item1"],
            surgeries=["surgery1", "surgery2", "surgery3"],
            ordering_policies={"item1": DeterministicConDOIPolicyV2("item1", constant_days=condoi_level)},
            item_delivery_times={"item1": GenerateDeterministic(lead_time)},
            initial_inventory={"item1": 0},
            outstanding_orders={"item1": set()},
            surgery_item_usage={"surgery1": {"item1": GenerateDeterministic(1)},
                                "surgery2": {"item1": GenerateDeterministic(2)},
                                "surgery3": {"item1": GenerateDeterministic(3)}
                                },
            surgery_stochastic_demand={"surgery1": GenerateDeterministic(3),
                                       "surgery2": GenerateDeterministic(2),
                                       "surgery3": GenerateDeterministic(1)
                                       },
            item_stochastic_demands={"item1": GenerateDeterministic(0)}
        )

        print("=================== START REPORT===================")
        print("conDOI Level:", condoi_level)
        print("lead time:", lead_time)
        run_stochastic_surgery_driven_simulation(config, show=True)
        print("======================== END ========================")

    if True:
        """ Booked Surgery Driven Simulation test"""
        condoi_level = 5
        lead_time = 2
        config = Booked_Surgery_Config(
            item_ids=["item1"],
            surgeries=["surgery1", "surgery2", "surgery3"],
            ordering_policies={"item1": DeterministicConDOIPolicyV2("item1", constant_days=condoi_level)},
            item_delivery_times={"item1": GenerateDeterministic(lead_time)},
            initial_inventory={"item1": 0},
            outstanding_orders={"item1": set()},
            surgery_item_usage={"surgery1": {"item1": GenerateDeterministic(1)},
                                "surgery2": {"item1": GenerateDeterministic(2)},
                                "surgery3": {"item1": GenerateDeterministic(3)}
                                },
            surgery_stochastic_demand={"surgery1": GenerateDeterministic(3),
                                       "surgery2": GenerateDeterministic(2),
                                       "surgery3": GenerateDeterministic(1)
                                       },
            surgery_booked_demand={"surgery1": GenerateDeterministic(2),
                                   "surgery2": GenerateDeterministic(1),
                                   "surgery3": GenerateDeterministic(3)
                                   },
            item_stochastic_demands={"item1": GenerateDeterministic(0)}
        )

        print("=================== START REPORT===================")
        print("conDOI Level:", condoi_level)
        print("lead time:", lead_time)
        run_booked_surgery_driven_simulation(config, show=True)
        print("======================== END ========================")




