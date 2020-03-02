# Custom packages
from src.timer import Timer
from src.workbreak import WorkBreak

from datetime import date, datetime


class Clock:
    def __init__(self):
        self.__brk = None
        self.__brk_callback = None
        self.__closure = None
        self.__closure_callback = None
        self.__time = datetime.now()
        self.__timers = set()

    @property
    def time(self):
        return self.__time

    def add_timer(self, timer):
        if not isinstance(timer, Timer):
            raise TypeError

        self.__timers.add(timer)

    def assign_break(self, brk, callback=None):
        if brk is None:
            self.__brk = None
            self.__brk_callback = None
        elif isinstance(brk, WorkBreak):
            self.__brk = brk
            self.__brk_callback = callback

    def assign_closure(self, closure, callback=None):
        if closure is None:
            self.__closure = None
            self.__closure_callback = None
        elif isinstance(closure, date):
            self.__closure = closure
            self.__closure_callback = callback

    def has_break(self):
        if self.__brk is not None:
            return True

        return False

    def is_break_time(self):
        if isinstance(self.__brk, WorkBreak) and self.__brk.start <= self.__time < self.__brk.end:
            return True

        return False

    def is_closure(self):
        if isinstance(self.__closure, date) and self.__closure == self.__time.date():
            return True

        return False

    def stop_timer(self, timer):
        if not isinstance(timer, Timer):
            raise TypeError

        if timer in self.__timers:
            self.__timers.remove(timer)
            timer.stop()

    def update(self):
        now = datetime.now()

        # Checks if the timers ought to be updated
        if len(self.__timers) > 0 and not (self.is_closure() or self.is_break_time()):
            dt = (now - self.__time).microseconds / pow(10, 6)  # Converts from microseconds to seconds

            for timer in self.__timers:
                timer.update(dt)

        self.__time = now  # Update the clock's current time

        # Checks if the break has ended
        if isinstance(self.__brk, WorkBreak) and self.__time >= self.__brk.end:
            self.__brk = None

            # Run callback function
            if self.__brk_callback is not None:
                self.__brk_callback()

        # Checks if the closure has ended
        if isinstance(self.__closure, date) and self.__time.date() > self.__closure:
            self.__closure = None

            # Run callback function
            if self.__closure_callback is not None:
                self.__closure_callback()
