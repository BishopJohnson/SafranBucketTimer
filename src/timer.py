from datetime import datetime
from math import floor


class Timer:
    def __init__(self, name, seconds=0, start_time=None):
        self.__name = name
        self.__seconds = seconds

        if start_time is not None:
            self.__start_time = start_time
        else:
            self.__start_time = datetime.now()

        self.__end_time = None
        self.__is_running = True

    @property
    def name(self):
        return self.__name

    @property
    def seconds(self):
        return floor(self.__seconds)

    @property
    def start_time(self):
        return self.__start_time

    @property
    def end_time(self):
        return self.__end_time

    @property
    def is_running(self):
        return self.__is_running

    def stop(self):
        if self.__is_running:
            self.__is_running = False
            self.__end_time = datetime.now()

    def update(self, dt):
        if self.__is_running:
            self.__seconds += dt
