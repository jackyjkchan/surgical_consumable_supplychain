import pandas as pd
import matplotlib.pyplot as plt

from scm_analytics import ScmAnalytics
from scm_analytics.config import lhs_config


item_id="38242"
case_service="Cardiac Surgery"

analytics = ScmAnalytics.ScmAnalytics(lhs_config)

