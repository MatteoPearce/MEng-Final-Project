from subprocess import call

def CallVAMPIRE(workdir_path: str = None, parallel: bool = False, debug_mode: bool = False) -> None:

    if workdir_path is not None:
        if parallel:
            call_word = "vampire-parallel"
        else:
            call_word = "vampire-serial"

        if debug_mode:
            call_word = call_word + "-debug"

        call(f'cd {workdir_path}; chmod +x {call_word}; ./{call_word}', shell=True)

#CallVAMPIRE("~/Desktop/VAMPIRE_WORKDIR")

