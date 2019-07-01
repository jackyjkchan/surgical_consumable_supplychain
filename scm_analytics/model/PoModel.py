from scm_analytics import Analytics


def assert_structure(df):
    mandatory_columns = [
        "po_id",
        "order_date",
        "po_class",
        "item_id",
        "qty",
        "unit_of_measure",
        "unit_price",
        "delivery_date",
        "qty_ea"]
    for col in mandatory_columns:
        assert(col in df)


def pre_process_columns(df):
    df['order_leadtime'] = df['delivery_date'] - df['order_date']
    return df


def lead_time_distribution(df, groupby=None, filters=[]):
    df = Analytics.process_filters(df, filters)
    return df["order_leadtime"].dt.days
