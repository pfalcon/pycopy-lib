import os


class SubprocessError(Exception):
    pass

class CalledProcessError(SubprocessError):
    pass


def check_call(cmd, shell=False):
    assert shell, "only shell=True is supported so far"
    res = os.system(cmd)
    if res:
        raise CalledProcessError(res >> 8)
