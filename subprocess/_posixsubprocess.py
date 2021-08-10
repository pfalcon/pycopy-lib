import sys
import gc
import os
import signal
import fcntl


_FD_CLOEXEC = getattr(fcntl, 'FD_CLOEXEC', 1)

try:
    MAXFD = os.sysconf("SC_OPEN_MAX")
except:
    MAXFD = 256


def _close_fds(fds_to_keep):
    start_fd = 3
    for fd in sorted(fds_to_keep):
        if fd >= start_fd:
            os.closerange(start_fd, fd)
            start_fd = fd + 1
    if start_fd <= MAXFD:
        os.closerange(start_fd, MAXFD)


def _set_cloexec(fd, cloexec):
    old = fcntl.fcntl(fd, fcntl.F_GETFD)
    if cloexec:
        fcntl.fcntl(fd, fcntl.F_SETFD, old | _FD_CLOEXEC)
    else:
        fcntl.fcntl(fd, fcntl.F_SETFD, old & ~_FD_CLOEXEC)


def cloexec_pipe():
    fds = os.pipe()
    _set_cloexec(fds[0], True)
    _set_cloexec(fds[1], True)
    return fds


def fork_exec(
    args, executable_list,
    close_fds, fds_to_keep, cwd, env_list,
    p2cread, p2cwrite, c2pread, c2pwrite,
    errread, errwrite,
    errpipe_read, errpipe_write,
    restore_signals, start_new_session, preexec_fn
):
    if 0:
        print(
            args, executable_list,
            close_fds, fds_to_keep, cwd, env_list,
            p2cread, p2cwrite, c2pread, c2pwrite,
            errread, errwrite,
            errpipe_read, errpipe_write,
            restore_signals, start_new_session, preexec_fn
        )

    # Pure Python implementation: It is not thread safe.
    # This implementation may deadlock in the child if your
    # parent process has any other threads running.

    gc_was_enabled = gc.isenabled()
    # Disable gc to avoid bug where gc -> file_dealloc ->
    # write to stderr -> hang.  See issue1336
    gc.disable()
    try:
        pid = os.fork()
    except:
        if gc_was_enabled:
            gc.enable()
        raise

    if pid == 0:
        # Child
        try:
            # Close parent's pipe ends
            if p2cwrite != -1:
                os.close(p2cwrite)
            if c2pread != -1:
                os.close(c2pread)
            if errread != -1:
                os.close(errread)
            os.close(errpipe_read)

            # Dup fds for child
            def _dup2(a, b):
                # dup2() removes the CLOEXEC flag but
                # we must do it ourselves if dup2()
                # would be a no-op (issue #10806).
                if a == b:
                    _set_cloexec(a, False)
                elif a != -1:
                    os.dup2(a, b)
            _dup2(p2cread, 0)
            _dup2(c2pwrite, 1)
            _dup2(errwrite, 2)

            # Close pipe fds.  Make sure we don't close the
            # same fd more than once, or standard fds.
            closed = set()
            for fd in [p2cread, c2pwrite, errwrite]:
                if fd > 2 and fd not in closed:
                    os.close(fd)
                    closed.add(fd)

            # Close all other fds, if asked for
            if fds_to_keep:
                _close_fds(fds_to_keep)


            if cwd is not None:
                os.chdir(cwd)

            # This is a copy of Python/pythonrun.c
            # _Py_RestoreSignals().  If that were exposed
            # as a sys._py_restoresignals func it would be
            # better.. but this pure python implementation
            # isn't likely to be used much anymore.
            if restore_signals:
                signals = ('SIGPIPE', 'SIGXFZ', 'SIGXFSZ')
                for sig in signals:
                    if hasattr(signal, sig):
                        signal.signal(getattr(signal, sig),
                                        signal.SIG_DFL)

            if start_new_session and hasattr(os, 'setsid'):
                os.setsid()

            if preexec_fn:
                preexec_fn()

            env = env_list
            if env is None:
                os.execvp(executable_list[0], args)
            else:
                os.execvpe(executable_list[0], args, env)

        except:
            try:
                exc_type, exc_value = sys.exc_info()[:2]
                if isinstance(exc_value, OSError):
                    errno_num = exc_value.errno
                else:
                    errno_num = 0
                message = '%s:%x:%s' % (exc_type.__name__,
                                        errno_num, exc_value)
                message = message.encode(errors="surrogatepass")
#                message = message.encode()
                os.write(errpipe_write, message)
            except Exception:
                # We MUST not allow anything odd happening
                # above to prevent us from exiting below.
                pass

        # This exitcode won't be reported to applications
        # so it really doesn't matter what we return.
        os._exit(255)

    # Parent
    if gc_was_enabled:
        gc.enable()
    return pid
