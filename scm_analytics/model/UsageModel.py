import pandas as pd
from scm_analytics import Analytics


def assert_structure(df):
    mandatory_columns = ["event_id",
                         "item_id",
                         "code_name",
                         "used_qty",
                         "unit_price",
                         "case_service",
                         "urgent_elective",
                         "booking_dt",
                         "start_dt",
                         "supply_issue_desc"]
    for col in mandatory_columns:
        assert (col in df)


def pre_process_columns(df):
    df['booking_leadtime'] = df['start_dt'] - df['booking_dt']
    return df


def item_usage_per_day_distribution(df, group_by=None, filters=[]):
    df = Analytics.process_filters(df, filters)
    df["start_date"] = df["start_dt"].apply(lambda x: x.date())
    start, end = min(df["start_date"]), max(df["start_date"])
    if group_by:
        df = df.groupby(group_by)
    date_df = pd.DataFrame()
    date_df["start_date"] = pd.date_range(start=start, end=end, freq='D')
    date_df["start_date"] = date_df["start_date"].apply(lambda x: x.date())

    def dist(g_df):
        g_df = g_df.groupby("start_date").agg({"used_qty": "sum"})
        data_df = date_df.join(g_df, on="start_date", how="left").fillna(0)
        return data_df["used_qty"].to_list()

    return df.apply(lambda f: dist(f))


def item_usage_per_week_distribution(usage_df, group_by=None, filters=[]):
    usage_df = Analytics.process_filters(usage_df, filters)
    usage_df["week"] = usage_df["start_dt"].apply(
        lambda x: "{0}-{1}".format(str(x.year - 1 if (x.month == 1 and x.week == 52) else x.year), str(x.week))
    )
    start, end = min(usage_df["start_dt"]), max(usage_df["start_dt"])
    if group_by:
        usage_df = usage_df.groupby(group_by)
    date_df = pd.DataFrame()
    date_df["start_date"] = pd.date_range(start=start, end=end, freq='W')
    date_df["week"] = date_df["start_date"].apply(
        lambda x: "{0}-{1}".format(str(x.year - 1 if (x.month == 1 and x.week == 52) else x.year), str(x.week))
    )
    date_df = date_df[["week"]]

    def dist(g_df):
        g_df = g_df.groupby("week").agg({"used_qty": "sum"})
        data_df = date_df.join(g_df, on="week", how="left").fillna(0)
        return data_df["used_qty"].to_list()

    return usage_df.apply(lambda f: dist(f))
