from subprocess import call
from subprocess import run
import time


def CallVAMPIRE(workdir_path: str = None, parallel: bool = False, debug_mode: bool = False, show_output: bool = False) -> None:

    if workdir_path is not None:
        if parallel:
            call_word = "vampire-parallel"
        else:
            call_word = "vampire-serial"

        if debug_mode:
            call_word = call_word + "-debug"

        start_time = time.time()
        if show_output:
            call(f'cd {workdir_path}; chmod +x {call_word}; ./{call_word}', shell=True)
        else:
            print("running simulation")
            output = run(f'cd {workdir_path}; chmod +x {call_word}; ./{call_word}', capture_output=True, shell=True).stdout
            print("simulation done")

        end_time = time.time()
        total_time = end_time - start_time
        if total_time < 1:
            print("VAMPIRE FAILED")

#CallVAMPIRE("~/Desktop/VAMPIRE_WORKDIR")

