import time
import subprocess, sys
from prepare import update_universe


def nightly_routine():
    while True:
        print("Starting Nightly Research...")
        update_universe()
        subprocess.run([sys.executable, "auto_optimize.py"], check=True)

        print("Strategy updated. Waiting for next market close...")
        time.sleep(86400)


if __name__ == "__main__":
    nightly_routine()
