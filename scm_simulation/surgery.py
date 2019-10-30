import numpy as np


class Surgery(object):
    """
    An immutable class

    id (str):
    label for surgery

    item_info {item_id: number}:
    information contribution to demand for item_id, used for policy that depends on information_process

    item_usages {item_id: NumberGenerator}:
    item usage model for each item. (Poisson, Binom, General_Dist). Used to generate random usage for items
    """
    __slots__ = ["id", "item_infos", "item_usages"]

    def __init__(self, id, item_infos, item_usages):
        """Constructor"""
        super(Surgery, self).__setattr__("id", id)
        super(Surgery, self).__setattr__("item_infos", item_infos)
        super(Surgery, self).__setattr__("item_usages", item_usages)

    def __str__(self):
        return self.id
