import signal
import time
import os

print(f"{os.getpid()=}")
print("sleeping for a while. test to see what exit code python returns for various signals")
time.sleep(1000)
