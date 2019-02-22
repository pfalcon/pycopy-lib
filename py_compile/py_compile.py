import os

def compile(file, cfile=None):
    cmdline = "mpy-cross %s" % file
    # For now, just hardcode -mcache-lookup-bc, as that's default for
    # Unix port.
    cmdline += " -mcache-lookup-bc"
    if cfile is not None:
        cmdline += " -o %s" % cfile
    res = os.system(cmdline)
    if res:
        raise OSError("Error running mpy-cross, rc=%d" % (res >> 8))
