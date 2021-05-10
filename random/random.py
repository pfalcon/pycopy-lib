from urandom import *


def randrange(start, stop=None):
    if stop is None:
        stop = start
        start = 0
    upper = stop - start
    bits = 0
    pwr2 = 1
    while upper > pwr2:
        pwr2 <<= 1
        bits += 1
    if bits == 0:
        return start
    while True:
        r = getrandbits(bits)
        if r < upper:
            break
    return r + start

def randint(start, stop):
    return randrange(start, stop + 1)

uniform = randint

def random():
    # single-precision float mantissa is 23 bits, add one to be safe
    return getrandbits(24) / (1<<24)

def shuffle(seq):
    l = len(seq)
    if l < 2:
        return
    for i in range(l):
        j = randrange(l)
        seq[i], seq[j] = seq[j], seq[i]

def choice(seq):
    if not seq:
        raise IndexError
    return seq[randrange(len(seq))]


class Random:
    @staticmethod
    def random():
        return random()

    @staticmethod
    def randrange(start, stop=None):
        return randrange(start, stop)

    @staticmethod
    def randint(start, stop):
        return randint(start, stop)

    uniform = randint

    @staticmethod
    def shuffle(seq):
        return shuffle(seq)

    @staticmethod
    def choice(seq):
        return choice(seq)

