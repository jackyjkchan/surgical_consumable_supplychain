import pickle
import plotly.graph_objects as go

### set up 1 ###
# lead_time = 2
# setup_cost = 0
# backlogging_cost = 1000
# information_horizon = 2
# df = pickle.load(open("publish/2020-03-06_leadtime_experiment.pickle", "rb"))
# print(df.iloc[0])
# print(set(df["backlogging_cost"]))

### set up 2 ###
lead_time = 0
setup_cost = 10
backlogging_cost = 1000
information_horizon = 2
df = pickle.load(open("publish/2020-03-05_setup_cost_experiment.pickle", "rb"))

### set up 3 ###
# lead_time = 0
# setup_cost = 0
# backlogging_cost = 1
# information_horizon = 2
# df = pickle.load(open("publish/2020-02-28_base_experiment.pickle", "rb"))
# df = pickle.load(open("publish/2020-07-07_base_experiment.pickle", "rb")) #b1

### set up 4 ###
# lead_time = 0
# setup_cost = 0
# backlogging_cost = 10
# information_horizon = 2
# df = pickle.load(open("publish/2020-02-28_base_experiment.pickle", "rb"))

### set up 5 ###
lead_time = 0
setup_cost = 10
backlogging_cost = 10
information_horizon = 2
df = pickle.load(open("publish/2022-04-23_setup_cost_experiment_1e-5_detailed.pickle", "rb"))

### set up 6 ###
# lead_time = 0
# setup_cost = 0
# backlogging_cost = 1000
# information_horizon = 2
# df = pickle.load(open("publish/2022-05-15_base_experiment_binom10_1e-5_detailed.pickle", "rb"))


### set up 7 ###
### Variance tuning experiment
# lead_time = 0
# setup_cost = 0
# backlogging_cost = 1000
# information_horizon = 2
# df = pickle.load(open("publish/2020-04-01_variance_experiment_n=3_merged.pickle", "rb"))
# usage_model = sorted(list(set(df["usage_model"])))[0]
# print(usage_model)
# df = df[df["usage_model"] == usage_model]

information_states0 = list(range(0, 11))
information_states1 = list(range(0, 11))

plot_data = df[(df["lead_time"] == lead_time) &
               (df["setup_cost"] == setup_cost) &
               (df["backlogging_cost"] == backlogging_cost) &
               (df["information_horizon"] == information_horizon) &
               (df["t"] == 20)
               ]

order_up_tos = []
reorder_pt = []
for information_state1 in information_states1:
    order_up_tos_row = []
    reorder_pt_row = []
    for information_state0 in information_states0:
        order_up_to = \
            plot_data[plot_data["information_state"] == (information_state0, information_state1)]["order_up_to"].iloc[0]
        base_stock = \
            plot_data[plot_data["information_state"] == (information_state0, information_state1)]["base_stock"].iloc[0]

        order_up_tos_row.append(order_up_to)
        reorder_pt_row.append(base_stock)

    order_up_tos.append(order_up_tos_row)
    reorder_pt.append(reorder_pt_row)

fig = go.Figure(go.Surface(
    x=information_states0,
    y=information_states1,
    z=order_up_tos,
    contours={
        "x": {"show": True, "size": 1, "start": 0, "end": 11},
        "y": {"show": True, "size": 1, "start": 0, "end": 11},
    },
    colorscale='ice'
))
fig.add_surface(x=information_states0,
                y=information_states1,
                z=reorder_pt,
                contours={
                    "x": {"show": True, "size": 1, "start": 0, "end": 11},
                    "y": {"show": True, "size": 1, "start": 0, "end": 11},
                },
                colorscale='ice'
                )

fig.update_scenes(xaxis_title_text='Information State[0]',
                  yaxis_title_text=r'Information State[1]',
                  zaxis_title_text=r'Units',
                  aspectratio={"x": 1, "y": 1, "z": 0.75},
                  camera_eye={"x": 0, "y": -1, "z": 0.5},
                  )

print(lead_time,
      setup_cost,
      backlogging_cost,
      information_horizon)
fig.show()
