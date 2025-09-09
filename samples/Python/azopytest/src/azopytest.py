import sys

# Add CUDA toolkit path
import os
cuda_path = os.getenv('CUDA_PATH')
if not cuda_path:
    print("CUDA_PATH environment variable not set or CUDA Toolkit is not installed")
    sys.exit()
os.add_dll_directory(os.environ['CUDA_PATH'] + r"\bin")

import argparse
from samples.nurse.sample import NurseSample
from samples.pbs.sample import PbsSample
from samples.tsp.sample import TspSample

# TODO: Must add Amazolve install directory to PYTHONPATH
#
# e.g. PYTHONPATH=C:\Amazolve\bin

import azopy

# TODO: Must set environment variable to point to Amazolve samples path (e.g. C:\Amazolve\samples)
# or hard code here manually.
#
azo_sample_path = os.getenv('AZO_SAMPLE_PATH')
if not azo_sample_path:
    print("AZO_SAMPLE_PATH environment variable not set")
    sys.exit()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Amazolve Python Tester and Samples.")
    parser.add_argument(
        "--run", 
        default = "debug", 
        help = "Solver run mode (either debug or release).")
    parser.add_argument(
        "--itest", 
        default = "tsp", 
        help = "Sample to run (nurse, tsp, or pbs).")
    parser.add_argument(
        "--tc", 
        default = "100", 
        help = "Thread count.")
    parser.add_argument(
        "--ss", 
        help = "Stop score - stops the solver when this score is reached.")
    parser.add_argument(
        "--st", 
        help = "Stop time - max time to run solver (in seconds).")
    parser.add_argument(
        "--device", 
        default = "0",
        help = "CUDA device id (default 0).")
    parser.add_argument(
        "--nurseinst", 
        default = "1",
        help = "(Specific to nurse sample). The DB instance to use (default 1 with a best score of 607).")

    args = parser.parse_args()

    # arg error checks
    if args.itest == "nurse" and not args.nurseinst:
        print("Missing nurseinst argument for nurse sample")

    config = azopy.SolverConfig()
    match args.itest:
        case "nurse":
            config.problem_file = os.path.join(azo_sample_path, "nurseProb", "nurse.json")
            config.data_path = os.path.join(azo_sample_path, "nurseProb", "dyndata", args.nurseinst)
            ns = NurseSample(os.path.join(azo_sample_path, "nurseDB", args.nurseinst), config.data_path)
            ns.create_dyndata()
        case "pbs":
            config.problem_file = os.path.join(azo_sample_path, "pbsProb", "pbs.json")
            config.data_path = os.path.join(azo_sample_path, "pbsProb", "dyndata")
            ps = PbsSample(os.path.join(azo_sample_path, "pbsDB"), config.data_path)
            ps.create_dyndata()
        case "tsp":
            config.problem_file = os.path.join(azo_sample_path, "tspProb", "tsp.json")
            config.data_path = os.path.join(azo_sample_path, "tspProb", "dyndata")
            ps = TspSample(config.data_path)
            ps.create_dyndata()

    config.device = int(args.device)
    config.debug = args.run == "debug"
    if args.ss:
        config.stop_score = int(args.ss)
    config.stop_seconds = int(args.st)

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
        print(f"{constraint.cid}: {constraint.cscore} ({constraint.ctime} ms)")

    print("")
