import random
import time
# helper methods taken from stackoverflow that will simplify date setting
def strTimeProp(start, end, f, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times fed in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, f))
    etime = time.mktime(time.strptime(end, f))

    ptime = stime + prop * (etime - stime)
    return time.strftime(f, time.localtime(ptime))


def randomDate(start, end, prop):
    return strTimeProp(start, end, '%Y-%m-%d %H:%M:%S', prop)

