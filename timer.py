from datetime import datetime


class Timer:
    def __init__(self):
        self.dt = None
        self.time = 0

    def current(self):
        seconds = (datetime.now() - self.dt).seconds

        # Checks if at least one second has passed
        if seconds > 0:
            self.time += seconds
            self.dt = datetime.now()  # Updates delta time

        return self.time

    def get_time(self):
        return self.time

    def reset(self):
        self.dt = datetime.now()

    def start(self):
        self.reset()
        self.time = 0
