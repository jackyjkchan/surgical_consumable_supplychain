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
    #sns.palplot(sns.color_palette("Blues"))
    colours = [
        '#08306b', '#08519c', '#2171b5'
    ]
    sns.set_style("whitegrid")

    def halfwidth(series):
        return 1.96 * np.std(series) / np.sqrt(len(series))
    item = "21920"

    #data = pd.read_pickle("publish/case_study/2020-04-20_parametric_case_study_full_inventory_500.pickle")
    data = pd.read_pickle("publish/case_study/2020-07-09_parametric_case_study_1686.pickle")
    data = pd.read_pickle("publish/case_study/2020-07-24_parametric_case_study_round3.pickle")

    data = data[(data["item_id"] == item) & (data["backlogging_cost"] == 1000) &  (data["lead_time"] == 1)]


    days = range(14, 21)
    # filtered_data = data[data["info_horizon"] == n]
    for day in days:
        data[day] = data["full_inventory_lvl"].apply(lambda x: x[day])

    data = pd.melt(data, id_vars=['seed', "info_horizon"], value_vars=days,
                   var_name='day', value_name="inventory_level")
    data["info_horizon"] = data["info_horizon"].apply(lambda x: int(x))

    data["Information Horizon"] = data["info_horizon"].apply(lambda x: "{}-ABI".format(str(x)))
    data["Inventory Level"] = data["inventory_level"]
    data["Day"] = data["day"]

    plt.figure(figsize=(5, 3))
    ax = sns.lineplot(x="Day", y="Inventory Level", data=data, markers=True, dashes=True, style="Information Horizon",
                      hue="Information Horizon", legend="brief", palette=colours)
    plt.tight_layout()
    handles, labels = ax.get_legend_handles_labels()
    box = ax.get_position()
    plt.xticks(days, ["Mon", "Tue",  "Wed", "Thu", "Fri", "Sat", "Sun"])
    plt.yticks(np.arange(5, 25 + 1, 5))

    #ax.set_position([box.x0, box.y0, box.width, box.height])
    #bbox_to_anchor=(1.35, 0.5)
    ax.legend(handles=handles[1:], labels=labels[1:], loc='lower center', ncol=3)

    ax.grid(False)

    plt.savefig("parametric_simulation_inventory_level_trace_{}.svg".format(item), format="svg")
    plt.savefig("parametric_simulation_inventory_level_trace_{}.eps".format(item), format="eps")
