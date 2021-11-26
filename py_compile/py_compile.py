import os

def compile(file, cfile=None):
    cmdline = "pycopy-cross %s" % file
    # For now, just hardcode -mcache-lookup-bc, as that's default for
    # Unix port.
    cmdline += " -mcache-lookup-bc"
    if cfile is not None:
        cmdline += " -o %s" % cfile
    else:
        cfile = file.rsplit(".", 1)[0] + ".mpy"
    res = os.system(cmdline)
    if res:
        raise OSError("Error running pycopy-cross, rc=%d" % (res >> 8))
    mtime = os.stat(file)[8]
    os.utime(cfile, (mtime, mtime))

if __name__ == "__main__":
    import sys
    for f in sys.argv[1:]:
        compile(f)
