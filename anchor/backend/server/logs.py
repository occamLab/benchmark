import contextlib, sys, os


@contextlib.contextmanager
def nostderr():
    """Low level stderr supression."""
    newstderr = os.dup(2)
    devnull = os.open("/dev/null", os.O_WRONLY)
    os.dup2(devnull, 2)
    os.close(devnull)
    yield
    os.dup2(newstderr, 2)


@contextlib.contextmanager
def nostdout():
    """Low level stdout supression."""
    newstderr = os.dup(1)
    devnull = os.open("/dev/null", os.O_WRONLY)
    os.dup2(devnull, 1)
    os.close(devnull)
    yield
    os.dup2(newstderr, 1)
