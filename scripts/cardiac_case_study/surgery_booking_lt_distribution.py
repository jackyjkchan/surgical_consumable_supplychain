import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st

from scm_analytics.model.SurgeryModel import surgeries_per_day_distribution, pre_process_columns
from scm_analytics import ScmAnalytics
from scm_analytics.config import lhs_config
import datetime

case_service = "Cardiac Surgery"

analytics = ScmAnalytics.ScmAnalytics(lhs_config)
orig_surgery_df = pre_process_columns(analytics.surgery_df)
orig_surgery_df = orig_surgery_df[orig_surgery_df["start_date"].notna()]
# surgery_df = surgery_df[surgery_df["start_date"] > datetime.date(2016, 1, 1)]
# surgery_df = surgery_df[surgery_df["start_date"] < datetime.date(2017, 1, 1)]
# surgery_df = surgery_df[surgery_df["urgent_elective"] == "Elective"]

case_services = set(orig_surgery_df["case_service"])
start_dates = [datetime.date(2016, 1, 1), datetime.date(2016, 7, 1), datetime.date(2017, 1, 1), datetime.date(2017, 7, 1)]
end_dates = [datetime.date(2016, 7, 1), datetime.date(2017, 1, 1), datetime.date(2017, 7, 1), datetime.date(2017, 12, 31)]

start_dates = [datetime.date(2016, 1, 1)]
end_dates = [datetime.date(2017, 1, 1)]


case_services.add("ALL")
for case_service in case_services:
    for start, end in zip(start_dates, end_dates):
        if case_service != "ALL":
            surgery_df = orig_surgery_df[orig_surgery_df["case_service"] == case_service]
        else:
            surgery_df = orig_surgery_df
        surgery_df = surgery_df[surgery_df["start_date"] > start]
        surgery_df = surgery_df[surgery_df["start_date"] < end]

        print(case_service)
        print(start)
        print(end)
        if len(surgery_df) < 200:
            continue
        if case_service == "Obstetrics/Gynecology":
            continue

        data = surgery_df["booking_leadtime"].apply(lambda x: x.days)
        data_to_plot = [21 if i > 20 else i for i in data]
        bins = list(range(22))

        fig, ax = plt.subplots(figsize=(15, 5))
        _, bins, patches = plt.hist(data_to_plot,
                                    bins=bins,
                                    color='C0',
                                    density=True,
                                    alpha=0.5,
                                    rwidth=0.96,
                                    label="Empirical")
        xlabels = list(np.array(bins, dtype='str'))
        xlabels[-1] = '20+'
        N_labels = len(xlabels)
        plt.xticks(list(range(21)) + [20.5])
        ax.set_xticklabels(xlabels)
        plt.legend()
        plt.title("Elective Surgery Booking Lead Time Distribution")
        plt.xlabel("Days")
        plt.ylabel("Probability")
        plt.savefig("surgeries_distribution_leadtime_{0}_{1}-{2}_Trunk.png".format(case_service, str(start), str(end)), format="png")

        ## data > 20 only
        data = surgery_df["booking_leadtime"].apply(lambda x: x.days)
        data_to_plot = list(filter(lambda x: x > 20, data))
        bins = list(range(max(data_to_plot)+2))

        fig, ax = plt.subplots(figsize=(15, 5))
        _, bins, patches = plt.hist(data_to_plot,
                                    bins=bins,
                                    color='C0',
                                    density=True,
                                    alpha=0.5,
                                    rwidth=0.96,
                                    label="Empirical")
        plt.legend()
        plt.title("Elective Surgery Booking Lead Time Distribution for Surgeries with LT > 20 only")
        plt.xlabel("Days")
        plt.ylabel("Probability")
        plt.savefig("surgeries_distribution_leadtime_{0}_{1}-{2}_GT20.png".format(case_service, str(start), str(end)),
                    format="png")

        # No filtering
        data = surgery_df["booking_leadtime"].apply(lambda x: x.days)
        data_to_plot = data
        bins = list(range(max(data_to_plot)+2))

        fig, ax = plt.subplots(figsize=(15, 5))
        _, bins, patches = plt.hist(data_to_plot,
                                    bins=bins,
                                    color='C0',
                                    density=True,
                                    alpha=0.5,
                                    rwidth=0.96,
                                    label="Empirical")
        plt.legend()
        plt.title("Elective Surgery Booking Lead Time Distribution for Surgeries No Truncating")
        plt.xlabel("Days")
        plt.ylabel("Probability")
        plt.savefig("surgeries_distribution_leadtime_{0}_{1}-{2}_No_Trunk.png".format(case_service, str(start), str(end)),
                    format="png")

        # fig, ax = plt.subplots(figsize=(9, 5))
        # surgery_df = surgery_df[surgery_df["booking_leadtime_days"] <= 2]
        # filters = [{"dim": "urgent_elective",
        #             "op": "eq",
        #             "val": "Elective"
        #             }]
        # dist_df = surgeries_per_day_distribution(surgery_df, day_group_by="is_weekday", filters=filters)
        # data = dist_df.set_index("is_weekday").loc[True]["data"]
        # bins = range(1 + int(max(data)))
        # fit_x = [x + 0.5 for x in bins]
        # n = int(max(data)) - 1
        # p = np.mean(data) / n
        # mean = np.mean(data)
        # plt.hist(data, bins=range(1 + int(max(data))),
        #          color='C0',
        #          density=True,
        #          alpha=0.5,
        #          rwidth=0.96,
        #          label="Empirical")
        # plt.vlines(fit_x, 0, st.poisson.pmf(bins, mean),
        #            color='C1',
        #            lw=5,
        #            alpha=0.5)
        # plt.plot(fit_x, st.poisson.pmf(bins, mean), "o",
        #          color='C1',
        #          ms=8,
        #          alpha=0.5,
        #          label="Poisson mean={0:0.2f}".format(mean))
        # plt.legend()
        # plt.title("Elective {0} With Booking LT <= 2 Distribution".format(case_service))
        # plt.xlabel("Surgeries Per Day")
        # plt.ylabel("Probability")
        # plt.savefig("surgeries_distribution_leadtime_{0}_{1}-{2}.png".format(case_service, str(start), str(end)), format="png")
