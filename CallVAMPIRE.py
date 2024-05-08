from subprocess import call
from subprocess import run
import time
import multiprocessing
import os

"""
INVOKE VAMPIRE 5.0.0 ATOMISTIC SIMULATOR>

Three compatible run modes:

    serial
    parallel
    debug
    
To speed up the simulation select show_output = False

Failure criteria is not a catchall. If when simulation fails to start up it will do so in <1s. 
"""

def CallVAMPIRE(workdir_path: str = None, parallel: bool = False, debug_mode: bool = False, show_output: bool = False) -> None:

    if os.path.exists(workdir_path): # working directory where vampire binary is located
        if parallel:
            call_word = "vampire-parallel"
        else:
            call_word = "vampire-serial"

        if debug_mode:
            call_word = call_word + "-debug" # only works if debug mode is compiled

        start_time = time.time() # timing used to catch vampire failures
        if show_output:
            if not parallel:
                call(f'cd {workdir_path}; chmod +x {call_word}; ./{call_word}', shell=True) # using call prints vampire output to console
            else:
                call(f'cd {workdir_path}; chmod +x {call_word}; mpirun -np {multiprocessing.cpu_count()-1} ./{call_word}', shell=True) # number of processors - 1
        else:
            print("running simulation") # print message because vampire output silent
            if not parallel:
                output = run(f'cd {workdir_path}; chmod +x {call_word}; ./{call_word}', capture_output=True, shell=True).stdout # using run hides vampire output
            else:
                output = run(f'cd {workdir_path}; chmod +x {call_word}; mpirun -np {multiprocessing.cpu_count()} ./{call_word}', capture_output=True, shell=True).stdout
            print("simulation done")

        end_time = time.time()
        total_time = end_time - start_time
        if total_time < 1: # heuristic failure detector
            print("VAMPIRE FAILED")

    else:
        print("VAMPIRE NOT FOUND")

