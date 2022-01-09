import time as time_

import attr


@attr.define
class Time:
    time: int
    klass: str = attr.ib(default=None)

    # custom field that stores system time when server time is received
    sys_time: int = int(time_.time())

    @staticmethod
    def serialize(**kwargs):
        return Time(sys_time=int(time_.time()), **kwargs)

    @property
    def diff(self):
        return self.sys_time - self.time
