import pandas as pd
import matplotlib.pyplot as plt

from scm_analytics import ScmAnalytics, config


item_id="38242"
case_service="Cardiac Surgery"

analytics = ScmAnalytics.ScmAnalytics(config.lhs_config)

usage_df = analytics.usage.df
usage_df = usage_df[usage_df["item_id"] == item_id]
usage_df = usage_df[usage_df["case_service"] == case_service]
usage_df = usage_df.drop_duplicates(subset=["event_id"])

surgery_df = analytics.surgery.df
surgery_df = surgery_df[surgery_df["case_service"] == case_service]
surgery_df = surgery_df[surgery_df["scheduled_procedures"].notna()]
surgery_df = surgery_df[surgery_df["event_id"].isin(set(analytics.usage.df["event_id"]))]
surgery_df = surgery_df.drop_duplicates(subset=["event_id"])
surgery_df = surgery_df.join(usage_df[["event_id", "used_qty"]].set_index("event_id"),
                                 on="event_id",
                                 how="left")
surgery_df["used_qty"] = surgery_df["used_qty"].fillna(0)
surgery_df["start_date"] = surgery_df["start_dt"].apply(lambda x: x.date())

start = min(surgery_df["start_date"])
end = max(surgery_df["start_date"])

po_df = analytics.po.df
po_df = po_df[po_df["item_id"] == item_id]
po_df["delivery_date"] = po_df["delivery_date"].apply(lambda x: x.date())
po_df = po_df[po_df["delivery_date"] >= start]
po_df = po_df[po_df["delivery_date"] <= end]


day_df = pd.DataFrame()
day_df["day"] = pd.date_range(start=start, end=end, freq='D')
day_df["day"] = day_df["day"].apply(lambda x: x.date())

day_df = day_df.join(surgery_df.groupby(["start_date"]).agg({"used_qty": "sum"}),
                                        on="day",
                                        how="left",
                                        rsuffix="usage").fillna(0)

day_df["received_qty"] = day_df.join(po_df.groupby(["delivery_date"]).agg({"qty_ea": "sum"}),
                                     on="day",
                                     how="left",
                                     rsuffix="delivery").fillna(0)["qty_ea"]

day_df["change"] = day_df["received_qty"] - day_df["used_qty"]
day_df["inventory_level"] = day_df["change"].cumsum()

day_df["inventory_level"] = day_df["inventory_level"] - 2*min(day_df["inventory_level"])

plt.step(day_df["day"], day_df["inventory_level"])
plt.show()