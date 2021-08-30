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
        self.is_stationary = True if isinstance(policy, dict) else False
        self.item_id = item_id
        self.policy = policy
        self.info_horizon = len(list(policy.keys())[0]) if self.is_stationary else len(list(policy[0].keys())[0])
        self.granularity = granularity
        self.max_states = tuple(max(state[i] for state in policy.keys()) for i in range(self.info_horizon)) \
            if self.is_stationary else \
            tuple(tuple(max(state[i] for state in p.keys()) for i in range(self.info_horizon)) for p in policy)

    def action(self, hospital):
        iid = self.item_id
        ts = range(hospital.clock, hospital.clock + self.info_horizon)
        # Extract info state from hospital for item using elective schedule
        info_state = list(sum(surgery.item_infos[iid] for surgery in hospital.full_elective_schedule[t]) for t in ts)
        info_state[0] = info_state[0] + sum(surgery.item_infos[iid] for surgery in hospital.curr_surgery_backlog)
        # Round to granularity
        info_state = tuple(round(info / self.granularity) * self.granularity for info in info_state)
        # Cap to policy max levels
        max_states_t = self.max_states if self.is_stationary else self.max_states[hospital.clock % 7]
        info_state = tuple(min(max_states_t[i], info_state[i]) for i in range(self.info_horizon))
        order_up_lvl, reorder_lvl = self.policy[info_state] if self.is_stationary \
            else self.policy[hospital.clock % 7][info_state]
        action = order_up_lvl - hospital.curr_inventory_position[iid] \
            if hospital.curr_inventory_position[iid] <= reorder_lvl else 0
        return action


class LAPolicy(OrderPolicy):

    def __init__(self, item_id, la_model):
        self.item_id = item_id
        self.la_model = la_model
        self.granularity = 1

    def action(self, hospital):
        iid = self.item_id
        ts = range(hospital.clock, min(hospital.clock + 14, hospital.max_periods-1))
        # Extract info state from hospital for item using elective schedule
        info_state = list(sum(surgery.item_infos[iid] for surgery in hospital.full_elective_schedule[t]) for t in ts)
        info_state[0] = info_state[0] + sum(surgery.item_infos[iid] for surgery in hospital.curr_surgery_backlog)
        # Round to granularity
        info_state = tuple(round(info / self.granularity) * self.granularity for info in info_state)
        # Cap to policy max levels
        x = hospital.curr_inventory_position[self.item_id]

        t_to_go = min(27, hospital.sim_time-hospital.clock)
        action = self.la_model.order_la(t_to_go, x, info_state)

        return action


class FixedSsPolicy(OrderPolicy):

    def __init__(self, item_id, order_up_lvl, reorder_lvl):
        self.item_id = item_id
        self.order_up_lvl = order_up_lvl
        self.reorder_lvl = reorder_lvl

    def action(self, hospital):
        iid = self.item_id
        qty = self.order_up_lvl if hospital.curr_inventory_position[iid] <= self.reorder_lvl else 0
        return qty
