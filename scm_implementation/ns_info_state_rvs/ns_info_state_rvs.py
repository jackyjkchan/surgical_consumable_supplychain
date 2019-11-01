import pacal
import pickle
import os


def load(fn):
    with open(fn, "rb") as f:
        p = pickle.load(f)
    return p


source_dir = "scm_implementation/ns_info_state_rvs"
elective_info_rvs = {fn.split(".")[0]: load(os.path.join(source_dir, "elective", fn))
                     for fn in os.listdir(os.path.join(source_dir, "elective"))}
emergency_info_rvs = {fn.split(".")[0]: load(os.path.join(source_dir, "emergency", fn))
                      for fn in os.listdir(os.path.join(source_dir, "emergency"))}

