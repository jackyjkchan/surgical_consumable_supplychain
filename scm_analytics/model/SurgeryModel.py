import pandas as pd
from scm_analytics import Analytics


def assert_structure(df):
    mandatory_columns = ["event_id",
                         "scheduled_procedures",
                         "completed_procedures",
                         "case_service",
                         "OR_delay_desc",
                         "start_dt",
                         "end_dt",
                         "case_dt",
                         "booking_dt",
                         "case_cart_id",
                         "urgent_elective"]
    for col in mandatory_columns:
        assert (col in df)


def pre_process_columns(df):
    df['booking_leadtime'] = df['case_dt'] - df['booking_dt']
    weekday_map = {0: "Monday",
                   1: "Tuesday",
                   2: "Wednesday",
                   3: "Thursday",
                   4: "Friday",
                   5: "Saturday",
                   6: "Sunday"}

    df['day_of_week'] = df['case_dt'].apply(lambda x:
                                            weekday_map[x.weekday()]
                                            if x.weekday() in weekday_map
                                            else "Unknown")
    df['month'] = df['case_dt'].apply(lambda x: str(x.month))
    df['surgery_duration'] = df["end_dt"] - df["start_dt"]
    return df


def add_preference_card_fill_feature(surgery_df, case_cart_df, item_id):
    surgery_df = surgery_df[surgery_df["event_id"].isin(case_cart_df["event_id"])]
    case_cart_df = case_cart_df[case_cart_df["item_id"] == item_id].drop_duplicates(keep="last")
    return surgery_df.join(case_cart_df[["event_id", "fill_qty"]].set_index("event_id"),
                           on="event_id",
                           how="left",
                           rsuffix="fill").fillna(0)


def lead_time_distribution(df, group_by=None, filters=[]):
    df = Analytics.process_filters(df, filters)
    return df["order_leadtime"].dt.days


def surgery_count_metric(df, group_by=None, filters=[]):
    """
    returns a df with count of number of surgeries for each group of the group by dimension.
    i.e. if group by case service, cardiac 5 meaning 5 surgeries total from cardiac department.
    """
    df = Analytics.process_filters(df, filters)
    return df[[group_by, "event_id"]] \
        .groupby([group_by]) \
        .agg({'event_id': 'nunique'}) \
        .reset_index() \
        .rename(columns={'event_id': 'metrix', group_by: 'dimension'})


def surgery_hours_metric(df, group_by=None, filters=[]):
    """
    df should be surgery_df
    returns df with total hours of surgeries in each group of the group by dimension.
    i.e. cardiac 10hours
    """
    df = Analytics.process_filters(df, filters)
    df = df[df["surgery_duration"].notna()]
    df = df[[group_by, "surgery_duration"]] \
        .groupby([group_by]) \
        .agg({'surgery_duration': 'sum'}) \
        .reset_index() \
        .rename(columns={'surgery_duration': 'metric', group_by: 'dimension'})
    # to convert from seconds to hours
    df["metric"] = df["metric"].apply(lambda x: x.days * 24 + x.seconds / 60)
    return df


def surgeries_per_day_distribution(df, group_by=None, filters=[]):
    df = Analytics.process_filters(df, filters)
    #df["start_date"] = df["start_dt"].apply(lambda x: x.date())
    start, end = min(df["start_date"]), max(df["start_date"])
    if group_by:
        df = df.groupby(group_by)

    def dist(g_df):
        g_df = g_df.groupby("start_date").agg({"event_id": "nunique"})
        data_df = pd.DataFrame()
        data_df["start_date"] = pd.date_range(start=start, end=end, freq='D')
        data_df["start_date"] = data_df["start_date"].apply(lambda x: x.date())
        data_df = data_df.join(g_df, on="start_date", how="left").fillna(0)
        print(data_df)
        return data_df["event_id"].to_list()
    return df.apply(lambda f: dist(f))
