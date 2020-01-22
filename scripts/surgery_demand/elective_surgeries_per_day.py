import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st
import statsmodels.datasets

from scm_analytics.model.SurgeryModel import surgeries_per_day_distribution, pre_process_columns
from scm_analytics import ScmAnalytics
from scm_analytics.config import lhs_config
import datetime

case_service = "Cardiac Surgery"

analytics = ScmAnalytics.ScmAnalytics(lhs_config)
surgery_df = pre_process_columns(analytics.surgery_df)
surgery_df = surgery_df[surgery_df["start_date"].notna()]
surgery_df = surgery_df[surgery_df["start_date"] > datetime.date(2016, 1, 1)]
filters = [{"dim": "case_service",
            "op": "eq",
            "val": case_service
            },
           {"dim": "urgent_elective",
            "op": "eq",
            "val": "Elective"
            }]

dist_df = surgeries_per_day_distribution(surgery_df, day_group_by="is_weekday", filters=filters)
data = dist_df.set_index("is_weekday").loc[True]["data"]
print(data)
bins = range(1 + int(max(data)))
binom_x = [x+0.5 for x in bins]
n = int(max(data))-1
print(n)
p = np.mean(data) / n
plt.hist(data, bins=range(1 + int(max(data))),
         color='C0',
         density=True,
         alpha=0.5,
         rwidth=0.96,
         label="Empirical")
plt.vlines(binom_x, 0, st.binom.pmf(bins, n, p),
           color='C1',
           lw=5,
           alpha=0.5)
plt.plot(binom_x, st.binom.pmf(bins, n, p), "o",
         color='C1',
         ms=8,
         alpha=0.5,
         label="Binomial n={0:d}, p={1:.2f}".format(n, p))
plt.legend()
plt.title("{0} Elective Surgeries Per Day on Weekdays".format(case_service))
plt.xlabel("Surgeries Per Day")
plt.ylabel("Probability")
plt.savefig("surgeries_per_day_{0}.png".format(case_service), format="png")


