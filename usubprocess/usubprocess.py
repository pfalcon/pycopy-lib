import builtins
import uos2 as os


PIPE = 1


class SubprocessError(Exception):
    pass

class CalledProcessError(SubprocessError):
    pass


class Popen:

    def __init__(self, args, stdin=None, stdout=None, shell=False):
        assert stdin is None
        assert stdout in (None, PIPE)
        self.stdin = self.stdout = self.stderr = None

        if stdout == PIPE:
            i_p, o_c = os.pipe()
        if stdin == PIPE:
            i_c, o_p = os.pipe()
        pid = os.fork()
        self.pid = pid
        if not pid:
            if stdin is not None:
                os.dup2(i_c, 0)
                os.close(i_c)
            if stdout is not None:
                os.dup2(o_c, 1)
                os.close(o_c)

            if shell:
                assert isinstance(args, str), "Only string args is supported"
                s = os.system(args)
                if s & 0xff:
                    s = 0x7f
                else:
                    s >>= 8
            else:
                assert isinstance(args, list), "Only list args is supported"
                s = os.execvp(args[0], args)

            os._exit(s)
        else:
            if stdout == PIPE:
                os.close(o_c)
                self.stdout = builtins.open(i_p, "rb")
            if stdin == PIPE:
                self.stdin = builtins.open(o_p, "wb")

    def communicate(self):
        _stderr = None
        _stdout = None
        if self.stdout:
            _stdout = self.stdout.read()
        return(_stdout, _stderr)

    def wait(self):
        returncode = os.waitpid(self.pid, 0)[1]
        assert returncode & 0xff == 0
        returncode >>= 8
        self.returncode = returncode
        return returncode


def check_call(args, shell=False):
    p = Popen(args, shell=shell)
    p.communicate()
    rc = p.wait()
    if rc:
        raise CalledProcessError(rc)


def check_output(args, shell=False):
    p = Popen(args, stdout=PIPE, shell=shell)
    output = p.communicate()[0]
    rc = p.wait()
    if rc:
        raise CalledProcessError(rc, output)
    return output
