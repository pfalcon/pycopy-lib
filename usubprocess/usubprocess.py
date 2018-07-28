import os


class SubprocessError(Exception):
    pass

class CalledProcessError(SubprocessError):
    pass


def check_call(cmd, shell=False):
    assert shell
    res = os.system(cmd)
    if res:
        raise CalledProcessError(res >> 8)
