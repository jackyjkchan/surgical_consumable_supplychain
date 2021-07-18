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
bins = range(int(max(data)))
binom_x = [x + 0.5 for x in bins]
n = int(max(data)) - 1
print(n)
p = np.mean(data) / n

fig = plt.figure(figsize=(4.5, 4))
from matplotlib.ticker import PercentFormatter
plt.gca().yaxis.set_major_formatter(PercentFormatter(1, decimals=0, symbol=''))
plt.tight_layout()
plt.gcf().subplots_adjust(bottom=0.15, left=0.15)
plt.hist(data, bins=range(1 + int(max(data))),
         color='#08306b',
         density=True,
         rwidth=0.96,
         label="Empirical")
plt.vlines(binom_x, 0, st.binom.pmf(bins, n, p),
           color='#a50f15',
           lw=5,
           alpha=0.5)
plt.plot(binom_x, st.binom.pmf(bins, n, p), "o",
         color='#a50f15',
         ms=8,
         label="Binomial Fit")
print("Binomial n={0:d}, p={1:.2f}".format(n, p))
plt.legend()
ax = plt.axes()
ax.set(xlabel='Surgeries per Day', ylabel='Probability (%)',
       title='');
# plt.savefig("surgeries_distribution_number_per_day_{0}.png".format(case_service), format="png")
plt.savefig("elective_surgeries_distribution_number_per_day_{0}.eps".format(case_service), format="eps")
plt.close()

fig = plt.figure(figsize=(4.5, 4))
plt.gca().yaxis.set_major_formatter(PercentFormatter(1, decimals=0, symbol=''))
plt.tight_layout()
plt.gcf().subplots_adjust(bottom=0.15, left=0.15)
filters = [{"dim": "case_service",
            "op": "eq",
            "val": case_service
            },
           {"dim": "urgent_elective",
            "op": "eq",
            "val": "Urgent"
            }]
data = surgeries_per_day_distribution(surgery_df, filters=filters)
bins = range( int(max(data)))
fit_x = [x + 0.5 for x in bins]
n = int(max(data)) - 1
p = np.mean(data) / n
mean = np.mean(data)
plt.hist(data, bins=range(1 + int(max(data))),
         color='#08306b',
         density=True,
         rwidth=0.96,
         label="Empirical")
plt.vlines(fit_x, 0, st.poisson.pmf(bins, mean),
           color='#a50f15',
           lw=5,
           alpha=0.5)
plt.plot(fit_x, st.poisson.pmf(bins, mean), "o",
         color='#a50f15',
         ms=8,
         label="Poisson Fit")
print("Poisson mean={0:0.2f}".format(mean))
plt.legend()
ax = plt.axes()
ax.set(xlabel='Surgeries per Day', ylabel='Probability (%)',
       title='');
plt.savefig("emergency_surgeries_distribution_number_per_day_{0}.eps".format(case_service), format="eps")
plt.close()
