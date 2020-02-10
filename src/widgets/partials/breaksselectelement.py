# Custom packages
from src.define import Days
from src.widgets.appwidget import AppWidget
from src.widgets.partials.selectelement import SelectElement

from functools import partial
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
from math import floor


Builder.load_file('src/kv/partials/breaksselectelement.kv')


class BreaksSelectElement(RelativeLayout, AppWidget):
    def __init__(self, app, *args, **kwargs):
        super(BreaksSelectElement, self).__init__()

        self._app = app
        self.__day = Days.MONDAY
        self.__hour = 12
        self.__minute = 0
        self.__period = 'AM'
        self.__weekday_elem = SelectElement(self._app,
                                            increment_callback=partial(self.__increment_day, 1),
                                            decrement_callback=partial(self.__increment_day, -1),
                                            size_hint_x=0.2)
        self.__hour_elem = SelectElement(self._app,
                                         increment_callback=partial(self.__increment_hour, 1),
                                         decrement_callback=partial(self.__increment_hour, -1),
                                         size_hint_x=0.2)
        self.__minute_elem = SelectElement(self._app,
                                           increment_callback=partial(self.__increment_minute, 1),
                                           decrement_callback=partial(self.__increment_minute, -1),
                                           size_hint_x=0.2)
        self.__period_elem = SelectElement(self._app,
                                           increment_callback=self.__toggle_period,
                                           decrement_callback=self.__toggle_period,
                                           size_hint_x=0.2)

        self.layout.add_widget(self.__weekday_elem)
        self.layout.add_widget(self.__hour_elem)
        self.layout.add_widget(self.__minute_elem)
        self.layout.add_widget(self.__period_elem)

    @property
    def day(self):
        return self.__day

    @property
    def hour(self):
        return self.__hour

    @property
    def hour_elem(self):
        return self.__hour_elem

    @property
    def minute(self):
        return self.__minute

    @property
    def minute_elem(self):
        return self.__minute_elem

    @property
    def period(self):
        return self.__period

    @property
    def period_elem(self):
        return self.__period_elem

    @property
    def weekday_elem(self):
        return self.__weekday_elem

    def notify(self):
        super(BreaksSelectElement, self).notify()

        self.__update_day_text()
        self.__update_hour_text()
        self.__update_minute_text()
        self.__update_period_text()

        pass

    def __increment_day(self, value):
        value = (self.__day.value + floor(value)) % (Days.SUNDAY.value + 1)  # Loops back or forth if necessary
        self.__day = Days(value)

        self.__update_day_text()

    def __increment_hour(self, value):
        value = floor(value)

        # Sets the hour to be within [1,...,12]
        if value > 0:
            self.__hour = (self.__hour + value) % 13

            if self.__hour == 0:
                self.__hour += 1
        else:
            self.__hour += value

            # Cycles back if necessary
            if self.__hour <= 0:
                self.__hour = 12 - (abs(self.__hour) % 12)

        self.__update_hour_text()

    def __increment_minute(self, value):
        value = floor(value)

        # Sets the minute to be within [0,...,59]
        if value > 0:
            self.__minute = (self.__minute + value) % 60
        else:
            self.__minute += value

            if self.__minute < 0:
                self.__minute = 60 - (abs(self.__minute) % 60)

        self.__update_minute_text()

    def __toggle_period(self):
        if self.__period == 'AM':
            self.__period = 'PM'
        else:
            self.__period = 'AM'

        self.__update_period_text()

    def __update_day_text(self):
        if self.__day == Days.MONDAY:
            text = 'Mon.'
        elif self.__day == Days.TUESDAY:
            text = 'Tue.'
        elif self.__day == Days.WEDNESDAY:
            text = 'Wed.'
        elif self.__day == Days.THURSDAY:
            text = 'Thu.'
        elif self.__day == Days.FRIDAY:
            text = 'Fri.'
        elif self.__day == Days.SATURDAY:
            text = 'Sat.'
        elif self.__day == Days.SUNDAY:
            text = 'Sun.'
        else:
            text = ''

        self.__weekday_elem.set_text(text)

    def __update_hour_text(self):
        self.__hour_elem.set_text(f'{self.__hour:02d}')

    def __update_minute_text(self):
        self.__minute_elem.set_text(f'{self.__minute:02d}')

    def __update_period_text(self):
        self.__period_elem.set_text(self.__period)
