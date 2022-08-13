import pickle

### set up 1 ###
#model = pickle.load(open("2022-04-09_k10_L1_policy_plot/2022-04-09_k10_L1_policy_plot_0_model.pickle", "rb"))
#model = pickle.load(open("publish/2022-04-23_setup_cost_experiment_1e-3_detailed_k5_b10_info2_model.pickle", "rb"))
#model = pickle.load(open("publish/2022-05-27_variance_experiment_k10_booking_bin_1_model.pickle", "rb"))
#model = pickle.load(open("publish/2022-05-15_base_experiment_binom10_1e-5_detailed_0_model.pickle", "rb"))
model = pickle.load(open("publish/2022-06-11_base_experiment_binom10_k10_b1000_1e-5_detailed_0_model.pickle", "rb"))

print("K:", model.k)
print("lead_time:", model.lead_time)
print("b:", model.b)
print("booking:", model.info_state_rvs)
print("trunk:", model.usage_model)


information_states0 = list(range(0, 11))
information_states1 = list(range(0, 11))

# information_states0 = list(range(0, 16))
# information_states1 = list(range(0, 16))


order_up_tos = []
reorder_pt = []
for information_state1 in information_states1:
    order_up_tos_row = []
    reorder_pt_row = []
    for information_state0 in information_states0:
        order_up_to = model.stock_up_level(20, (information_state0, information_state1))
        base_stock = model.base_stock_level(20, (information_state0, information_state1))

        order_up_tos_row.append(order_up_to)
        reorder_pt_row.append(base_stock)

    order_up_tos.append(order_up_tos_row)
    reorder_pt.append(reorder_pt_row)

import plotly.graph_objects as go


fig = go.Figure(go.Surface(
    x=information_states0,
    y=information_states1,
    z=order_up_tos,
    contours={
        "x": {"show": True, "size": 1, "start": 0, "end": 16},
        "y": {"show": True, "size": 1, "start": 0, "end": 16},
    },
    colorscale='ice'
))
fig.add_surface(x=information_states0,
                y=information_states1,
                z=reorder_pt,
                contours={
                    "x": {"show": True, "size": 1, "start": 0, "end": 16},
                    "y": {"show": True, "size": 1, "start": 0, "end": 16},
                },
                colorscale='ice'
                )

fig.update_scenes(xaxis_title_text='Information State[0]',
                  yaxis_title_text=r'Information State[1]',
                  zaxis_title_text=r'Units',
                  aspectratio={"x": 1, "y": 1, "z": 0.75},
                  camera_eye={"x": 0, "y": -1, "z": 0.5},
                  )
fig.show()
