import pandas as pd
import numpy as np

from os import path
from scm_analytics import ScmAnalytics
from scm_analytics.config import lhs_config

def lhs_etl_routine():
    cache_path = 'C:\\Users\Jacky\Google Drive\MASc\workspace\inventory_supplychain_model\cache'
    local_cache_path = path.join(cache_path, "lhs_raw")
    dump_data_model_path = path.join(cache_path, "lhs_data_modelv2")

    po_df = pd.read_pickle(path.join(local_cache_path, "po_df"))
    hmms_po_df = pd.read_pickle(path.join(local_cache_path, "hmms_po_df"))
    surgery_df = pd.read_pickle(path.join(local_cache_path, "surgery_df"))
    case_cart_df = pd.read_pickle(path.join(local_cache_path, "case_cart_df"))
    usage_df = pd.read_pickle(path.join(local_cache_path, "usage_df"))
    item_catalog_df = pd.read_pickle(path.join(local_cache_path, "item_catalog_df"))

    case_cart_df = case_cart_df[case_cart_df["SchEventId"].isin(set(usage_df["SchEventId"]))]

    po_df["PO_DATE"] = pd.to_datetime(po_df["PO_DATE"])
    po_df["LAST_RCV_DATE"] = pd.to_datetime(po_df["LAST_RCV_DATE"])
    po_df["PO_NO"] = po_df["PO_NO"].astype(str)
    po_df = po_df[po_df["QTY"].notna()]
    po_df = po_df[po_df["UNIT PRICE"].notna()]

    po_rename = {
        "PO_NO":            "po_id",
        "PO_DATE":          "order_date",
        "PO_CLASS_CD":      "po_class",
        "ITEM_NO":          "item_id",
        "QTY":              "qty",
        "UM_CD":            "unit_of_measure",
        "UNIT PRICE":       "unit_price",
        "LAST_RCV_DATE":    "delivery_date",
        "QTY_RCV_TO_DATE":  "qty_received"
    }
    po_df = po_df.rename(columns=po_rename)
    po_df["stock_status"] = False

    hmms_po_df["REQ_DATE"] = pd.to_datetime(hmms_po_df["REQ_DATE"])
    #hmms_po_df["LAST_RCV_DATE"] = pd.to_datetime(po_df["LAST_RCV_DATE"])
    hmms_po_df["REQ_NO"] = hmms_po_df["REQ_NO"].astype(str).apply(lambda x: "hmms_{0}".format(x))
    hmms_po_df = hmms_po_df[hmms_po_df["QTY"].notna()]
    hmms_po_df = hmms_po_df[hmms_po_df["UNIT PRICE"].notna()]

    hmms_po_rename = {
        "REQ_NO": "po_id",
        "REQ_DATE": "order_date",
        "ITEM_NO": "item_id",
        "QTY": "qty",
        "UM_CD": "unit_of_measure",
        "UNIT PRICE": "unit_price"
        #"LAST_RCV_DATE": "delivery_date",
        #"QTY_RCV_TO_DATE": "qty_received"
    }
    hmms_po_df = hmms_po_df.rename(columns=hmms_po_rename)
    hmms_po_df["delivery_date"] = hmms_po_df["order_date"]
    hmms_po_df["item_id"] = hmms_po_df["item_id"].astype(str)
    hmms_po_df["stock_status"] = True

    po_df = pd.concat([po_df, hmms_po_df])[["po_id",
                                            "item_id",
                                            "qty",
                                            "order_date",
                                            "delivery_date",
                                            "po_class",
                                            "unit_of_measure",
                                            "unit_price",
                                            "stock_status"]]


    surgery_rename = {
        "SchEventId":                           "event_id",
        "AllScheduledProcedures":               "scheduled_procedures",
        "AllProcedures":                        "completed_procedures",
        "CaseService":                          "case_service",
        "Cancellation/DelayDueToSupplyIssue":   "supply_issue_desc",
        "ORDelayDesc":                          "OR_delay_desc",
        "ProcedureStartDtTm":                   "start_dt",
        "ProcedureStopDtTm":                    "end_dt",
        "CaseDate":                             "case_dt",
        "BookingDtTm":                          "booking_dt",
        "CASE_CART_ID":                         "case_cart_id",
        "UrgentVsElective":                     "urgent_elective"
    }
    surgery_df = surgery_df.rename(columns=surgery_rename)
    surgery_df["event_id"] = surgery_df["event_id"].values.astype(np.int64).astype(str)
    surgery_df = surgery_df[surgery_df["scheduled_procedures"].notna()]
    surgery_df["procedures"] = surgery_df["scheduled_procedures"].apply(lambda val:
                                                                       set([p.strip().lower() for p in
                                                                            val.split(",")])
                                                                       )

    case_cart_rename = {
        "SchEventId":   "event_id",
        "Item_id":      "item_id",
        "FILL_QTY":     "fill_qty",
        "OPEN_QTY":     "open_qty",
        "HOLD_QTY":     "hold_qty"
    }

    case_cart_df = case_cart_df.rename(columns=case_cart_rename)
    case_cart_df["event_id"] = case_cart_df["event_id"].values.astype(str)
    case_cart_df["item_id"] = case_cart_df["item_id"].values.astype(str)
    case_cart_df["case_cart_id"] = case_cart_df["case_cart_id"].values.astype(str)

    usage_rename = {
        "SchEventId":       "event_id",
        "Item_Number":      "item_id",
        "exp_code_name":    "code_name",
        "Requisition_Qty":  "used_qty"
    }
    usage_df = usage_df.rename(columns=usage_rename)
    usage_df["event_id"] = usage_df["event_id"].values.astype(str)
    usage_df["item_id"] = usage_df["item_id"].values.astype(str)

    item_cataog_rename = {
        "Item_No":                              "item_id",
        "Surginet Flag (interface to Cerner)":  "surginet_flag",
        "Unit Of Measure 1":                    "unit1",
        "Price 1":                              "price1",
        "Qty 1":                                "qty1",
        "Unit Of Measure 2":                    "unit2",
        "Price 2":                              "price2",
        "Qty 2":                                "qty2",
        "Unit Of Measure 3":                    "unit3",
        "Price 3":                              "price3",
        "Qty 3":                                "qty3",
        "Unit of Measure 4":                    "unit4",
        "Price 4":                              "price4",
        "Qty 4" :                               "qty4",
        "Unit of Measure 5":                    "unit5",
        "Price 5":                              "price5",
        "Stock Or Non Stock":                   "stock_nonstock"
    }
    item_catalog_df = item_catalog_df.rename(columns=item_cataog_rename)
    item_catalog_df["item_id"] = item_catalog_df["item_id"].values.astype(str)

    # filter out items, keep only items shared between po, catalog and usage
    usage_items = set(usage_df["item_id"])
    po_items = set(po_df["item_id"])
    catalog_items = set(item_catalog_df["item_id"])
    common_items = usage_items.intersection(po_items.intersection(catalog_items))

    usage_df = usage_df[usage_df["item_id"].isin(common_items)]
    po_df = po_df[po_df["item_id"].isin(common_items)]
    item_catalog_df = item_catalog_df[item_catalog_df["item_id"].isin(common_items)]

    # add scheduled procedures to case_cart
    case_cart_df = case_cart_df.join(surgery_df[["event_id",
                                                 "scheduled_procedures",
                                                 "case_service"
                                                 ]].set_index("event_id"),
                                     on="event_id",
                                     how="left",
                                     rsuffix="surgery")

    # normalize usage data
    usage_df = usage_df.join(item_catalog_df[["item_id", "price1"]].set_index("item_id"),
                             on='item_id',
                             how="left",
                             rsuffix="_catalog").rename(columns={"price1": "unit_price"})
    usage_df = usage_df.join(
                surgery_df[["event_id",
                            "case_service",
                            "urgent_elective",
                            "booking_dt",
                            "start_dt",
                            "supply_issue_desc",
                            "OR_delay_desc",
                            "scheduled_procedures"]
                           ].set_index("event_id"),
                on='event_id',
                how="left",
                rsuffix="_surgery")

    # build unit conversion lookup for items using item catalog
    qty2_conv_df = item_catalog_df[["item_id", "unit2", "qty1"]]
    qty3_conv_df = item_catalog_df[["item_id", "unit3", "qty1", "qty2"]]
    qty4_conv_df = item_catalog_df[["item_id", "unit4", "qty1", "qty2", "qty3"]]
    qty5_conv_df = item_catalog_df[["item_id", "unit5", "qty1", "qty2", "qty3", "qty4"]]
    qty2_conv_df["to_ea"] = qty2_conv_df["qty1"]
    qty3_conv_df["to_ea"] = qty3_conv_df["qty1"] * qty3_conv_df["qty2"]
    qty4_conv_df["to_ea"] = qty4_conv_df["qty1"] * qty4_conv_df["qty2"] * qty4_conv_df["qty3"]
    qty5_conv_df["to_ea"] = qty5_conv_df["qty1"] * qty5_conv_df["qty2"] * qty5_conv_df["qty3"] * qty5_conv_df["qty4"]
    qty2_conv_df["from_unit"] = qty2_conv_df["unit2"]
    qty3_conv_df["from_unit"] = qty3_conv_df["unit3"]
    qty4_conv_df["from_unit"] = qty4_conv_df["unit4"]
    qty5_conv_df["from_unit"] = qty5_conv_df["unit5"]
    qty2_conv_df = qty2_conv_df[["item_id", "from_unit", "to_ea"]]
    qty3_conv_df = qty3_conv_df[["item_id", "from_unit", "to_ea"]]
    qty4_conv_df = qty4_conv_df[["item_id", "from_unit", "to_ea"]]
    qty5_conv_df = qty5_conv_df[["item_id", "from_unit", "to_ea"]]
    conv_df = pd.concat([qty2_conv_df ,qty3_conv_df, qty4_conv_df, qty5_conv_df])
    po_df = po_df.join(conv_df.set_index(["item_id", "from_unit"]),
               on=["item_id", "unit_of_measure"],
               how="left",
               rsuffix="conv")
    po_df["to_ea"].fillna(1, inplace=True)
    po_df["qty_ea"] = po_df["qty"] * po_df["to_ea"]

    po_df.to_pickle(path.join(dump_data_model_path, "po_df"))
    usage_df.to_pickle(path.join(dump_data_model_path, "usage_df"))
    case_cart_df.to_pickle(path.join(dump_data_model_path, "case_cart_df"))
    item_catalog_df.to_pickle(path.join(dump_data_model_path, "item_catalog_df"))
    surgery_df.to_pickle(path.join(dump_data_model_path, "surgery_df"))
    return


if __name__=="__main__":
    lhs_etl_routine()
    analytics = ScmAnalytics(lhs_config)