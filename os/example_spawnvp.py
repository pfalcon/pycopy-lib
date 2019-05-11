import os
import time


print("Executing ls -l with P_NOWAIT:")
pid = os.spawnvp(os.P_NOWAIT, "ls", ["ls", "-l"])
print("pid:", pid)

time.sleep(1)

print("Executing ls -l with P_WAIT:")
rc = os.spawnvp(os.P_WAIT, "ls", ["ls", "-l3214"])
print("rc:", rc)

print("Executing cat with P_WAIT, waiting for signal:")
print("(ps for cat and kill it)")
rc = os.spawnvp(os.P_WAIT, "cat", ["cat"])
print("rc:", rc)
