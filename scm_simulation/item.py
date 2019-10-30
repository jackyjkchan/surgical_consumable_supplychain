import numpy as np


class Item(object):
    """
    An immutable class representing a surgical consumable.
    Useful helper functions for running simulations where all surgeries have the same usage model for the same item.
    i.e. all surgeries use item123 according to Poisson usage model.

    id (str):
    label for item

    usage_model (scm_opt.model.UsageModel):
    Usage model for mapping item demand info_state to raw item demand.
    """
    __slots__ = ["id", "usage_model"]

    def __init__(self, item_id, usage_model):
        """Constructor"""
        super(Item, self).__setattr__("id", item_id)
        super(Item, self).__setattr__("usage_model", usage_model)

    def __str__(self):
        return self.id

    def __hash__(self):
        return hash(self.id)

    def random(self, o):
        self.usage_model.random(o)
