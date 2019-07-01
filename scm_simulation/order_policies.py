import numpy as np


class OrderPolicy:
    def action(self, hospital):
        return 0


class POUTPolicyWithoutSchedule(OrderPolicy):
    def __init__(self, item_id, beta, level):
        self.item_id = item_id
        self.level = level
        self.beta = beta

    def action(self, clock, hospital):
        expected_demand = 0
        k = int(round(hospital.order_lead_times[self.item_id].mean()))
        if self.item_id in hospital.item_stochastic_demands:
            expected_demand += hospital.item_stochastic_demands[self.item_id].mean()
        for surgery in hospital.surgeries:
            expected_surgeries = hospital.surgery_stochastic_demand[surgery].mean()
            expected_surgeries += hospital.booked_surgery_stochastic_demand[surgery].mean()
            if self.item_id in hospital.surgery_item_usage[surgery]:
                expected_item_usage = hospital.surgery_item_usage[surgery][self.item_id].mean()
                expected_demand += expected_item_usage * expected_surgeries
        inv = hospital.inventory[self.item_id]
        wip = 0
        if clock + 15 < len(hospital.historical_deliveries[self.item_id]):
            wip += sum(hospital.historical_deliveries[self.item_id][clock + 1:clock + 15])
        elif clock + 1 < len(hospital.historical_deliveries[self.item_id]):
            wip += sum(hospital.historical_orders[self.item_id][clock + 1:])
        orderqty = expected_demand + self.beta * (self.level + expected_demand * k - (inv + wip))
        return max(0, orderqty)


class POUTPolicy(OrderPolicy):
    def __init__(self, item_id, beta, level):
        self.item_id = item_id
        self.level = level
        self.beta = beta

    def action(self, clock, hospital):
        expected_demand = 0
        k = int(round(hospital.order_lead_times[self.item_id].mean()))
        if self.item_id in hospital.item_stochastic_demands:
            expected_demand += hospital.item_stochastic_demands[self.item_id].mean()
        for surgery in hospital.surgeries:
            expected_surgeries = hospital.surgery_stochastic_demand[surgery].mean()
            if len(hospital.surgery_schedule[surgery]) > clock + k:
                expected_surgeries += np.mean(hospital.surgery_schedule[surgery][clock:clock + k])
            else:
                expected_surgeries += np.mean(hospital.surgery_schedule[surgery][clock:])
            if self.item_id in hospital.surgery_item_usage[surgery]:
                expected_item_usage = hospital.surgery_item_usage[surgery][self.item_id].mean()
                expected_demand += expected_item_usage * expected_surgeries
        inv = hospital.inventory[self.item_id]
        wip = 0
        if clock+15 < len(hospital.historical_deliveries[self.item_id]):
            wip += sum(hospital.historical_deliveries[self.item_id][clock+1:clock+15])
        elif clock+1 < len(hospital.historical_deliveries[self.item_id]):
            wip += sum(hospital.historical_orders[self.item_id][clock+1:])
        orderqty = int(round(expected_demand + self.beta * (self.level + expected_demand * k - (inv + wip))))
        return max(0, orderqty)

class DeterministicConDOIPolicy(OrderPolicy):

    def __init__(self, item_id, constant_days=5):
        self.item_id = item_id
        self.constant_days = constant_days

    def action(self, clock, hospital):
        expected_demand = 0
        if self.item_id in hospital.item_stochastic_demands:
            expected_demand += hospital.item_stochastic_demands[self.item_id].mean()
        for surgery in hospital.surgeries:
            if self.item_id in hospital.surgery_item_usage[surgery]:
                expected_surgeries = hospital.surgery_stochastic_demand[surgery].mean()
                expected_item_usage = hospital.surgery_item_usage[surgery][self.item_id]
                expected_demand += expected_surgeries * expected_item_usage

        delivery_time = hospital.order_lead_times[self.item_id].mean()
        order_up_level = int(expected_item_usage * delivery_time * self.constant_days)
        outstanding_orders = sum(hospital.historical_deliveries[self.item_id][clock + 1:]) \
            if len(hospital.historical_deliveries[self.item_id]) > (clock + 1) \
            else 0

        qty = order_up_level - hospital.inventory[self.item_id] - outstanding_orders

        return max(0, qty)


class DeterministicConDOIPolicyV2(OrderPolicy):

    def __init__(self, item_id, constant_days=5):
        self.item_id = item_id
        self.constant_days = constant_days

    def action(self, clock, hospital):
        k = self.constant_days
        delivery_time = hospital.order_lead_times[self.item_id].mean()
        expected_demand = 0
        if self.item_id in hospital.item_stochastic_demands:
            expected_demand += hospital.item_stochastic_demands[self.item_id].mean()
        for surgery in hospital.surgeries:
            horizon = int(round(k+delivery_time))
            expected_surgeries = hospital.surgery_stochastic_demand[surgery].mean()
            expected_surgeries += np.mean(hospital.surgery_schedule[surgery][clock: clock+horizon]) \
                if len(hospital.surgery_schedule[surgery]) > clock+horizon \
                else np.mean(hospital.surgery_schedule[surgery][clock:])
            if self.item_id in hospital.surgery_item_usage[surgery]:
                expected_item_usage = hospital.surgery_item_usage[surgery][self.item_id].mean()
                expected_demand += expected_surgeries * expected_item_usage

        order_up_level = int((k + delivery_time) * expected_demand)
        if len(hospital.historical_deliveries[self.item_id]) > (clock + 14):
            outstanding_orders = sum(hospital.historical_deliveries[self.item_id][clock + 1: clock + 14])
        elif len(hospital.historical_deliveries[self.item_id]) > (clock + 1):
            outstanding_orders = sum(hospital.historical_deliveries[self.item_id][clock + 1:])
        else:
            outstanding_orders = 0

        qty = order_up_level - hospital.inventory[self.item_id] - outstanding_orders
        return max(0, qty)


class DeterministicConDOIPolicyV2WithoutSchedule(OrderPolicy):
    """ This version of the conDOI policy does not have access to the actual surgery schedule and will only rely on
        the expected value of surgery demand.
    """
    def __init__(self, item_id, constant_days=5):
        self.item_id = item_id
        self.constant_days = constant_days

    def action(self, clock, hospital):
        k = self.constant_days
        delivery_time = hospital.order_lead_times[self.item_id].mean()
        expected_demand = 0
        if self.item_id in hospital.item_stochastic_demands:
            expected_demand += hospital.item_stochastic_demands[self.item_id].mean()
        for surgery in hospital.surgeries:
            expected_surgeries = hospital.surgery_stochastic_demand[surgery].mean()
            expected_surgeries += hospital.booked_surgery_stochastic_demand[surgery].mean()
            if self.item_id in hospital.surgery_item_usage[surgery]:
                expected_item_usage = hospital.surgery_item_usage[surgery][self.item_id].mean()
                expected_demand += expected_surgeries * expected_item_usage

        order_up_level = int((k + delivery_time) * expected_demand)
        if len(hospital.historical_deliveries[self.item_id]) > (clock + 14):
            outstanding_orders = sum(hospital.historical_deliveries[self.item_id][clock + 1: clock + 14])
        elif len(hospital.historical_deliveries[self.item_id]) > (clock + 1):
            outstanding_orders = sum(hospital.historical_deliveries[self.item_id][clock + 1:])
        else:
            outstanding_orders = 0

        qty = order_up_level - hospital.inventory[self.item_id] - outstanding_orders
        return max(0, qty)
