from scm_analytics import Analytics


def assert_structure(df):
    mandatory_columns = [
        "case_cart_id",
        "event_id",
        "item_id",
        "fill_qty",
        "open_qty",
        "hold_qty"]
    for col in mandatory_columns:
        assert (col in df)
