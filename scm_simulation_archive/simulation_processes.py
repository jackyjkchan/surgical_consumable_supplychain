def book_surgeries(env, hospital, booking_lead_time=14):
    """Process: Generates random number of surgeries to book K days into the future. This process assumes that at every
    period, we will book all surgeries K periods away. This is a simplification of having surgeons make their surgery
    schedules known 2 weeks in advance.
    """
    while True:
        yield env.timeout(1)

        for surgery in hospital.surgeries:
            num_surgeries = int(hospital.booked_surgery_stochastic_demand[surgery].gen())
            if len(hospital.surgery_schedule[surgery]) > env.now + booking_lead_time:
                hospital.surgery_schedule[surgery][env.now + booking_lead_time] += num_surgeries


def item_demand_from_surgeries_with_backorders(env, hospital):
    """
    Process: This process is responsible for consuming items that are used by surgeries.
    This process accounts for item consumption of both urgent and elective surgeries.
    Number of scheduled surgery at env.now is recorded in hospital.surgery_schedule[surgery][env.now]
    Number of urgent surgery is generated using hospital.surgery_stochastic_demand[surgery].gen()
    Number of item_id consumed by a surgery is randomly generated by calling the RNG
    hospital.surgery_item_usage[surgery][item_id].gen() the number of surgeries that is realized.
    with_backorders allows the inventory level to go negative, stock outs are not recorded.
    """
    while True:
        yield env.timeout(1)

        for surgery in hospital.surgeries:
            num_surgeries = round(hospital.surgery_stochastic_demand[surgery].gen())
            num_surgeries += hospital.surgery_schedule[surgery][env.now]
            for item_id in hospital.item_ids:
                d = 0
                d += sum(hospital.surgery_item_usage[surgery][item_id].gen() for i in range(0, num_surgeries))
                hospital.historical_demand[item_id][env.now] += d
                hospital.inventory[item_id] -= d


def item_demand_from_surgeries(env, hospital):
    """
    Process: This process is responsible for consuming items that are used by surgeries.
    This process accounts for item consumption of both urgent and elective surgeries.
    Number of scheduled surgery at env.now is recorded in hospital.surgery_schedule[surgery][env.now]
    Number of urgent surgery is generated using hospital.surgery_stochastic_demand[surgery].gen()
    Number of item_id consumed by a surgery is randomly generated by calling the RNG
    hospital.surgery_item_usage[surgery][item_id].gen() the number of surgeries that is realized.
    no backorders, inventory goes not go negative and demand is considered to be lost.
    """
    while True:
        yield env.timeout(1)

        for surgery in hospital.surgeries:
            num_surgeries = int(hospital.surgery_stochastic_demand[surgery].gen())
            num_surgeries += hospital.surgery_schedule[surgery][env.now]
            for item_id in hospital.item_ids:
                d = 0
                d += sum(hospital.surgery_item_usage[surgery][item_id].gen() for i in range(0, num_surgeries))
                hospital.historical_demand[item_id][env.now] += d
                if hospital.inventory[item_id] < d:
                    hospital.inventory[item_id] = 0
                    hospital.stockouts[item_id].append(env.now)
                else:
                    hospital.inventory[item_id] -= d


def item_demand(env, item_demand_generator, hospital):
    """
    Process: This process consumes items from the inventory based on raw demand distribution of item_demand.
    item_demand_generator is a dictionary {item_id: RNG_obj}
    No backorders in this version of the process
    """
    while True:
        yield env.timeout(1)

        for item_id in hospital.item_ids:
            d = item_demand_generator[item_id].gen()
            hospital.historical_demand[item_id][env.now] += d
            if hospital.inventory[item_id] < d:
                hospital.inventory[item_id] = 0
                hospital.stockouts[item_id].append(env.now)
            else:
                hospital.inventory[item_id] -= d


def item_demand_with_backorders(env, item_demand_generator, hospital):
    """
    Process: This process consumes items from the inventory based on raw demand distribution of item_demand.
    item_demand_generator is a dictionary {item_id: RNG_obj}
    Backorders enabled, inventory allowed to go negative, stock outs are not recorded.
    """
    while True:
        yield env.timeout(1)

        for item_id in hospital.item_ids:
            d = item_demand_generator[item_id].gen()
            hospital.historical_demand[item_id][env.now] += d
            hospital.inventory[item_id] -= d


def ship_order(env, item_id, qty, delivery_time, hospital):
    """
    DEPRECATED: This process is being removed due to a minor timing bug. Order of events differ from when lead time is 1
    vs when lead time is larger than 1. When lead time is larger than 1, this event will be scheduled first for that
    time step. However if lead time is 1, it will be scheduled just after demand and order placing events.
    This is generally not a problem as lead time is generally greater than 1 but this inconsistency has been addressed
    by the receive order process.
    Process: qty amount of item_id taking ship_time to arrive at the hospital.
    created by place_order process
    """
    while True:
        order_time = env.now
        yield env.timeout(delivery_time)
        hospital.inventory[item_id] += qty
        hospital.orders[item_id].remove((order_time, qty))
        hospital.historical_deliveries[item_id][env.now] += qty
        env.exit()


def remove_order(env, item_id, qty, delivery_time, hospital):
    """
    Process: Replacement for Deprecated ship_order process. This just removes the order from the pending order set.
    This is necessary for policies to determine amount of outstanding order correctly.
    """
    while True:
        order_time = env.now
        yield env.timeout(delivery_time)
        hospital.orders[item_id].remove((order_time, qty))
        env.exit()


def receive_order(env, hospital):
    """ Process:
    """
    while True:
        yield env.timeout(1)

        for item_id in hospital.item_ids:
            qty = hospital.historical_deliveries[item_id][env.now]
            hospital.inventory[item_id] += hospital.historical_deliveries[item_id][env.now]
            #print("time:", env.now, "inv:", hospital.inventory[item_id])


def place_order(env, ordering_policies, item_delivery_times, hospital):
    """Process: decision maker placing orders by implementing a given policy by calling policy.action(hospital)"""
    while True:
        yield env.timeout(1)
        for item_id in hospital.item_ids:
            order_qty = ordering_policies[item_id].action(env.now, hospital)
            hospital.orders[item_id].add((env.now, order_qty))
            hospital.historical_orders[item_id][env.now] += order_qty
            delivery_time = item_delivery_times[item_id].gen()
            if env.now + delivery_time < len(hospital.historical_deliveries[item_id]):
                hospital.historical_deliveries[item_id][env.now + delivery_time] += order_qty


def hospital_bookkeeping(env, hospital):
    """Process: hospital does book keeping at EOD and tracks values they care about
     inventory level
     more to come...
     """
    while True:
        yield env.timeout(1)

        for item_id in hospital.item_ids:
            hospital.historical_inventory_levels[item_id][env.now]+=hospital.inventory[item_id]
