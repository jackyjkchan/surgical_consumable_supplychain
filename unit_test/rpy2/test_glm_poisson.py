import pandas as pd
import numpy as np
import os

import rpy2.robjects as robjects
import rpy2.robjects.numpy2ri

from rpy2.robjects import pandas2ri
from scm_analytics import ScmAnalytics, Analytics
from statsmodels.api import families
from rpy2.robjects.packages import importr


base = importr('base')
stats = importr('stats')
broom = importr('broom')


pandas2ri.activate()
robjects.numpy2ri.activate()


data_pre = pd.read_csv(os.path.join("r_scripts", "test_data.csv"))
data_post = pd.read_csv(os.path.join("r_scripts", "test_data2.csv"))
print(data_pre)
results = stats.glm("y ~ . -1", data=pandas2ri.py2ri(data_pre), family=stats.poisson())
r = broom.tidy_lm(results)
df = pd.DataFrame({name: np.asarray(r.rx(name))[0] for name in r.names})
df.to_csv(os.path.join("unit_test", "rpy2", "rpy2_results.csv"))
print(df)
fitted_y = list(stats.fitted(results))

y = data_pre["y"]
y_bar = np.mean(y)
ss_tot = sum((y_bar - y) ** 2)
ss_res = sum((fitted_y - y) ** 2)
r2 = 1 - ss_res / ss_tot

print(r2)