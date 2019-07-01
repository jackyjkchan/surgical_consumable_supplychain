import pandas as pd
from os import path


class ScmAnalytics():

    def __init__(self, configs):

        self.config = configs

        cached_df_path = configs["cached_df_path"]
        self.po_df = pd.read_pickle(path.join(cached_df_path, "po_df"))
        self.usage_df = pd.read_pickle(path.join(cached_df_path, "usage_df"))
        self.case_cart_df = pd.read_pickle(path.join(cached_df_path, "case_cart_df"))
        self.item_catalog_df = pd.read_pickle(path.join(cached_df_path, "item_catalog_df"))
        self.surgery_df = pd.read_pickle(path.join(cached_df_path, "surgery_df"))
