import time


_PASSTHRU = ("sleep", "clock", "localtime")

for f in _PASSTHRU:
    globals()[f] = getattr(time, f)


def sleep_ms(t):
    time.sleep(t / 1000)

def sleep_us(t):
    time.sleep(t / 1000000)
