# Custom packages
from src.workbreak import WorkBreak

from datetime import datetime


class Clock:
    def __init__(self):
        self.__brk = None
        self.__brk_callback = None
        self.__now = datetime.now()
        self.__timer = 0
        self.__timer_end_time = None
        self.__timer_running = False
        self.__timer_start_time = None

    def assign_break(self, brk, callback=None):
        if isinstance(brk, WorkBreak):
            self.__brk = brk
            self.__brk_callback = callback

    def has_break(self):
        if self.__brk is not None:
            return True

        return False

    def is_break_time(self):
        if isinstance(self.__brk, WorkBreak) and self.__brk.start <= self.__now < self.__brk.end:
            return True

        return False

    def start_timer(self):
        self.__timer = 0
        self.__timer_end_time = None
        self.__timer_start_time = datetime.now()
        self.__timer_running = True

    def stop_timer(self):
        self.__timer_end_time = datetime.now()
        self.__timer_running = False

    def time(self):
        return self.__now

    def timer_end_time(self):
        return self.__timer_end_time

    def timer_start_time(self):
        return self.__timer_start_time

    def timer_time(self):
        return round(self.__timer)

    def update(self):
        now = datetime.now()

        # Checks if the timer ought to be updated
        if self.__timer_running and not self.is_break_time():
            self.__timer += (now - self.__now).microseconds / pow(10, 6)  # Converts from microseconds to seconds

        self.__now = now  # Update the current time

        # Checks if the break has ended
        if isinstance(self.__brk, WorkBreak) and self.__now >= self.__brk.end:
            self.__brk = None

            # Run callback function
            if self.__brk_callback is not None:
                self.__brk_callback()
