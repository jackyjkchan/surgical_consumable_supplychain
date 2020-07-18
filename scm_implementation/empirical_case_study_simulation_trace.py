import seaborn as sns;
import matplotlib.pyplot as plt

sns.set()
import pandas as pd
import numpy as np
import plotly

"""
Elective and emergency surgeries per day are empirically generated
Surgery definition are empirically generated (random sampling from all historical surgeries)
Surgery item usage are based on historical
"""

if __name__ == "__main__":
    plotly.io.orca.config.executable = 'C:\\Users\\Jacky\\AppData\\Local\\Programs\\orca\\orca.exe'


    def halfwidth(series):
        return 1.96 * np.std(series) / np.sqrt(len(series))


    #data = pd.read_pickle("publish/case_study/2020-04-20_parametric_case_study_full_inventory_500.pickle")
    data = pd.read_pickle("publish/case_study/2020-07-09_parametric_case_study_1686.pickle")

    days = range(14, 14 + 12 * 7)
    # filtered_data = data[data["info_horizon"] == n]
    for day in days:
        data[day] = data["full_inventory_lvl"].apply(lambda x: x[day])

    data = pd.melt(data, id_vars=['seed', "info_horizon"], value_vars=days,
                   var_name='day', value_name="inventory_level")
    data["info_horizon"] = data["info_horizon"].apply(lambda x: int(x))

    data["Info Horizon"] = data["info_horizon"]
    data["Inventory Level"] = data["inventory_level"]
    data["Day"] = data["day"]

    plt.figure(figsize=(10, 4))
    ax = sns.lineplot(x="Day", y="Inventory Level", data=data, markers=True, dashes=True, style="Info Horizon",
                      hue="Info Horizon", legend="full", palette="Set1")
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.85, box.height])
    ax.legend(loc='center right', bbox_to_anchor=(1.25, 0.5), ncol=1)
    plt.savefig("parametric_simulation_inventory_level_trace.svg", format="svg")
