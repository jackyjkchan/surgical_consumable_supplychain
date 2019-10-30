from scm_simulation.hospital import Hospital, SurgeryDemandProcess
from scm_simulation.item import Item
from scm_simulation.surgery import Surgery
from scm_simulation.rng_classes import GeneratePoisson, GenerateFromSample, GenerateDeterministic
from scm_simulation.order_policy import AdvancedInfoSsPolicy
"""
Simple test case replicating the numerical experiments for mdp.
No emergencies
Daily demand for elective surgeries is 1 or 2 with equal probability. 
Daily demand for emergency surgeries is 0 with probability of 1.
Surgery usage of items is Poisson 8
"""

item1 = "item1"
policy = {
    (1, 1, 1): (22, 6),
    (1, 1, 2): (19, 7),
    (1, 2, 1): (12, 5),
    (1, 2, 2): (28, 5),
    (2, 1, 1): (30, 15),
    (2, 1, 2): (27, 15),
    (2, 2, 1): (21, 14),
    (2, 2, 2): (36, 14)
}
policy = {item1: AdvancedInfoSsPolicy(item1, policy)}

order_lt = {item1: GenerateDeterministic(0)}
surgery1 = Surgery(
    "surgery1",
    {"item1": 1},
    {"item1": GeneratePoisson(8)}
)

elective_process = SurgeryDemandProcess([surgery1],
                                        GenerateFromSample([1, 2]),
                                        weekday_only=False)
emergency_process = SurgeryDemandProcess([surgery1],
                                         GenerateDeterministic(0))

hospital = Hospital([item1],
                    [surgery1],
                    policy,
                    order_lt,
                    emergency_process,
                    elective_process,
                    warm_up=10,
                    sim_time=10000,
                    end_buffer=5)

hospital.run_simulation()
hospital.trim_data()
