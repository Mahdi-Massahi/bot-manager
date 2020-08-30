import subprocess
import os

command = f"cd {os.path.dirname(__file__)} && Rscript Test.R --no-save"

try:
    print("Starting...")
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, preexec_fn=os.setsid)
    proc.wait(timeout=4.8)
    print("Ending...")
    if not proc.returncode == 0:
        raise Exception("Process has non-zero exit")
    else:
        print(f"Successfully ran R code subprocess. (pid={proc.pid})")

except Exception as err:
    print(f"Failed to ran R code subprocess. Error message: {err}")
