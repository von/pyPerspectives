"""Asyncore loop() with overall timeout"""

from asyncore import poll, poll2, socket_map

import time

def loop_with_timeout(timeout=30.0,
                      use_poll=False,
                      map=None,
                      count=None):
    """Modified version of asyncore.loop() where timeout reflects total time allowed.

    Instead of being timeout for select, timeout is the total time
    loop will run before returning.
    """
    if map is None:
        map = socket_map

    if use_poll and hasattr(select, 'poll'):
        poll_fun = poll2
    else:
        poll_fun = poll

    stop_time = time.time() + timeout

    if count is None:
        while map:
            timeout = stop_time - time.time()
            if timeout <= 0.0:
                break
            poll_fun(timeout, map)

    else:
        while map and count > 0:
            timeout = stop_time - time.time()
            if timeout <= 0.0:
                break
            poll_fun(timeout, map)
            count = count - 1
