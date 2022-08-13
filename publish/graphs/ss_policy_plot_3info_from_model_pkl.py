import pickle
import plotly.graph_objects as go
### set up 1 ###
#model = pickle.load(open("2022-04-09_k10_L1_policy_plot/2022-04-09_k10_L1_policy_plot_0_model.pickle", "rb"))

model = pickle.load(open("publish/2022-04-23_setup_cost_experiment_1e-3_detailed_k5_b10_info3_model.pickle", "rb"))

information_states0 = list(range(0, 11))
information_states1 = list(range(0, 11))
information_states2 = list(range(0, 11))


for information_state0 in information_states0:
    order_up_tos = []
    reorder_pt = []
    for information_state2 in information_states2:
        order_up_tos_row = []
        reorder_pt_row = []
        for information_state1 in information_states1:
            order_up_to = model.stock_up_level(20, (information_state0, information_state1, information_state2))
            base_stock = model.base_stock_level(20, (information_state0, information_state1, information_state2))

            order_up_tos_row.append(order_up_to)
            reorder_pt_row.append(base_stock)

        order_up_tos.append(order_up_tos_row)
        reorder_pt.append(reorder_pt_row)

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

    fig.update_scenes(xaxis_title_text='Information State[1]',
                      yaxis_title_text=r'Information State[2]',
                      zaxis_title_text=r'Units',
                      aspectratio={"x": 1, "y": 1, "z": 0.75},
                      camera_eye={"x": 0, "y": -1, "z": 0.5},
                      )
    fig.show()
    fig.write_html(f"info0_{information_state0}_ss_plot.html")
