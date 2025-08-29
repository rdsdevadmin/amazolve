import os

# Must add CUDA toolkit path
os.add_dll_directory(os.environ['CUDA_PATH'] + r"\bin")

# Must add Amazolve install directory to PYTHONPATH when running outside of IDE
# set PYTHONPATH=C:\Amazolve\Install

import azopy

if __name__ == "__main__":

    config = azopy.SolverConfig()
    config.problem_file = "C:\\Amazolve\\samples\\nurseProb\\nurse.json"
    config.data_path = "C:\\Amazolve\\samples\\nurseProb\\dyndata\\1\\"
    config.debug = False
    config.thread_count = 1536
    config.stop_score = 607
    config.stop_seconds = 120
    config.stop_no_change = 20

    solver = azopy.Solver()
    result = solver.solve(config)

    print("")
    print(f"Score  : \t{result.score}")
    print(f"Stop   : \t{result.stop_reason}")
    print(f"Time   : \t{result.time_taken}")
    print("")
    print(f"R Count: \t{result.resource_count}")
    print(f"T Count: \t{result.time_count}")
    print(f"S Count: \t{result.state_count}")

    print("")
    print("Atoms: ")
    for res_row in result.atoms:
        print(res_row)

    print("")
    print("Constraints: ")
    for constraint in result.constraints:
        print(f"{constraint.cid}: {constraint.cscore}")

    print("")
