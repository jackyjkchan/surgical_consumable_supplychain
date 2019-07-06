from scm_analytics import ScmAnalytics
from scm_analytics.config import lhs_config
from os import path

analytics = ScmAnalytics.ScmAnalytics(lhs_config)
cached_df_path = lhs_config["cached_df_path"]

surgery_df = analytics.surgery_df
usage_df = analytics.usage_df

surgery_df["start_date"] = surgery_df["start_dt"].apply(lambda x: x.date())
usage_df["start_date"] = usage_df["start_dt"].apply(lambda x: x.date())

surgery_df.to_pickle(path.join(cached_df_path, "surgery_df"))
usage_df.to_pickle(path.join(cached_df_path, "usage_df"))
