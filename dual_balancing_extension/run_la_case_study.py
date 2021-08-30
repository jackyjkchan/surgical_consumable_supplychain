from scm_implementation import empirical_case_study_simulation
import sys


if __name__ == "__main__":
    #item_ids = ["47320", "1686", "21920", "38197", "82099"]
    rep = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    item_id = str(sys.argv[2]) if len(sys.argv) > 2 else "47320"
    backlogging_cost = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
    info = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    lt = int(sys.argv[5]) if len(sys.argv) > 5 else 0

    args = (item_id, backlogging_cost, info, lt, rep)
    # item_id, b, n, lt, seed = args
    empirical_case_study_simulation.run_la_policy(args)
