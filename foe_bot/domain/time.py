import time as time_

from attr import field, define


@define
class Time:
    time: int = field()
    klass: str = field(default=None)

    # custom field that stores system time when server time is received
    sys_time: int = field(default=int(time_.time()))

    @property
    def diff(self):
        return self.sys_time - self.time
