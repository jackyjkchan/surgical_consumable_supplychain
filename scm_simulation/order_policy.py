class OrderPolicy:
    def action(self, hospital):
        return 0


class FixedOrderUpToPolicy(OrderPolicy):

    def __init__(self, item_id, order_level=5):
        self.item_id = item_id
        self.order_up_lvl = order_level

    def action(self, hospital):
        qty = self.order_up_lvl - hospital.curr_inventory_position[self.item_id]
        return max(0, qty)


class AdvancedInfoSsPolicy(OrderPolicy):

    def __init__(self, item_id, policy={}, granularity=1):
        self.item_id = item_id
        self.policy = policy
        self.info_horizon = len(list(policy.keys())[0])
        self.granularity = granularity
        self.max_states = tuple(max(state[i] for state in policy.keys()) for i in range(self.info_horizon))

    def action(self, hospital):
        iid = self.item_id
        ts = range(hospital.clock, hospital.clock+self.info_horizon)
        # Extract info state from hospital for item using elective schedule
        info_state = (sum(surgery.item_infos[iid] for surgery in hospital.full_elective_schedule[t]) for t in ts)
        # Round to granularity
        info_state = tuple(round(info/self.granularity)*self.granularity for info in info_state)
        # Cap to policy max levels
        info_state = tuple(min(self.max_states[i], info_state[i]) for i in range(self.info_horizon))
        order_up_lvl, reorder_lvl = self.policy[info_state]
        qty = order_up_lvl if hospital.curr_inventory_position[iid] <= reorder_lvl else 0
        return qty


class FixedSsPolicy(OrderPolicy):

    def __init__(self, item_id, order_up_lvl, reorder_lvl):
        self.item_id = item_id
        self.order_up_lvl = order_up_lvl
        self.reorder_lvl = reorder_lvl

    def action(self, hospital):
        iid = self.item_id
        qty = self.order_up_lvl if hospital.curr_inventory_position[iid] <= self.reorder_lvl else 0
        return qty
