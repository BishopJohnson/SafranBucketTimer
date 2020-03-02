# Custom packages
from src.define import Views
from src.widgets.appwidget import AppWidget
from src.widgets.partials.selectelement import SelectElement

from datetime import date
from dateutil.relativedelta import relativedelta
from functools import partial
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label


Builder.load_file('src/kv/breaksclosureswidget.kv')


class BreaksClosuresWidget(FloatLayout, AppWidget):
    def __init__(self, app):
        super(BreaksClosuresWidget, self).__init__()

        self.__app = app

        now = date.today()
        self.__closures = set()
        self.__closures_added = set()
        self.__closures_removed = set()
        self.__date = date(now.year, now.month, 1)
        self.__month_elem = SelectElement(self.__app,
                                          increment_callback=partial(self.__increment_month, 1),
                                          decrement_callback=partial(self.__increment_month, -1),
                                          orientation='horizontal',
                                          size_hint=(0.6, 0.1))

        self.add_widget(self.__month_elem)
        self.__month_elem.pos_hint = {'x': 0.2, 'y': 0.875}

        self.back_btn.bind(on_release=partial(self.__app.gui.open_view, Views.BREAKS_MENU))
        self.apply_btn.bind(on_release=self.apply_closures)

    def apply_closures(self, *args, **kwargs):
        for day in self.__closures_added:
            closure = {
                'year': day.year,
                'month': day.month,
                'day': day.day
            }

            self.__app.add_closure(closure)

        for day in self.__closures_removed:
            closure = {
                'year': day.year,
                'month': day.month,
                'day': day.day
            }

            self.__app.remove_closure(closure)

        self.__closures_added.clear()    # Update the closure data before handling the UI
        self.__closures_removed.clear()  #

        self.notify()

    def notify(self):
        super(BreaksClosuresWidget, self).notify()

        self.__update_closures()  # Update the closure data before handling the UI

        self.__update_apply_button()
        self.__update_calender()
        self.__update_month_text()

        pass

    def __add_closure(self, day):
        if isinstance(day, date):
            # Checks if the closure was set to be removed
            if day in self.__closures_removed:
                self.__closures_removed.remove(day)
            else:
                self.__closures_added.add(day)

        self.__update_apply_button()

    def __increment_month(self, value):
        self.__date += relativedelta(months=value)  # TODO: Handle the year 9999.

        self.notify()

    def __remove_closure(self, day):
        if isinstance(day, date):
            # Checks if the closure was set to be added
            if day in self.__closures_added:
                self.__closures_added.remove(day)
            else:
                self.__closures_removed.add(day)

        self.__update_apply_button()

    def __update_apply_button(self):
        if len(self.__closures_added) > 0 or len(self.__closures_removed) > 0:
            self.apply_btn.disabled = False
        else:
            self.apply_btn.disabled = True

    def __update_calender(self):
        self.layout.clear_widgets()

        year = self.__date.year
        month = self.__date.month
        month_start = date(year, month, 1)
        month_end = date(year, month, 1) + relativedelta(months=1, days=-1)  # TODO: Handle the year 9999.

        day = 1 - month_start.weekday()  # Offsets days to start on the proper weekday

        # Labels for the weekdays
        self.layout.add_widget(Label(text='Mon.', bold=True, font_size=20))
        self.layout.add_widget(Label(text='Tue.', bold=True, font_size=20))
        self.layout.add_widget(Label(text='Wed.', bold=True, font_size=20))
        self.layout.add_widget(Label(text='Thu.', bold=True, font_size=20))
        self.layout.add_widget(Label(text='Fri.', bold=True, font_size=20))
        self.layout.add_widget(Label(text='Sat.', bold=True, font_size=20))
        self.layout.add_widget(Label(text='Sun.', bold=True, font_size=20))

        tiles = self.layout.rows * self.layout.cols

        for tile in range(7, tiles):
            if month_start.day <= day <= month_end.day:
                btn_day = date(year, month, day)
                text = '{}'.format(day)
                btn = BreaksClosuresDayBtn(day=btn_day,
                                           activate_callback=partial(self.__add_closure, btn_day),
                                           deactivate_callback=partial(self.__remove_closure, btn_day),
                                           text=text)

                # Checks if the button ought to start as activated
                if btn_day in self.__closures or btn_day in self.__closures_added:
                    btn.toggle_active()

                self.layout.add_widget(btn)
            else:
                btn = BreaksClosuresDayBtn(text='')
                btn.disabled = True

                self.layout.add_widget(btn)

            day += 1

    def __update_closures(self):
        self.__closures.clear()

        closures = self.__app.data_cache['closures']

        for closure in closures:
            self.__closures.add(date(closure['year'], closure['month'], closure['day']))

    def __update_month_text(self):
        if self.__date.month == 1:
            text = 'Jan.'
        elif self.__date.month == 2:
            text = 'Feb.'
        elif self.__date.month == 3:
            text = 'Mar.'
        elif self.__date.month == 4:
            text = 'Apr.'
        elif self.__date.month == 5:
            text = 'May'
        elif self.__date.month == 6:
            text = 'June'
        elif self.__date.month == 7:
            text = 'July'
        elif self.__date.month == 8:
            text = 'Aug.'
        elif self.__date.month == 9:
            text = 'Sep.'
        elif self.__date.month == 10:
            text = 'Oct.'
        elif self.__date.month == 11:
            text = 'Nov.'
        elif self.__date.month == 12:
            text = 'Dec.'
        else:
            text = ''

        self.__month_elem.set_text('{} {}'.format(text, self.__date.year))


class BreaksClosuresDayBtn(Button):
    def __init__(self,
                 *args,
                 day=None,
                 is_holiday=False,
                 activate_callback=None,
                 deactivate_callback=None,
                 text='',
                 **kwargs):
        super(BreaksClosuresDayBtn, self).__init__(text=text)

        self.__is_active = False

        if type(is_holiday) is bool:
            self.__is_holiday = is_holiday

            if self.__is_holiday:
                self.background_color = (1, 0.6, 0.6, 1)
        else:
            raise TypeError

        if isinstance(day, date):
            self.__day = day
        else:
            self.__day = None

        if callable(activate_callback):
            self.__activate_callback = activate_callback
        else:
            self.__activate_callback = None

        if callable(deactivate_callback):
            self.__deactivate_callback = deactivate_callback
        else:
            self.__deactivate_callback = None

    @property
    def is_active(self):
        return self.__is_active

    @property
    def is_holiday(self):
        return self.__is_holiday

    @property
    def day(self):
        return self.__day

    def on_release(self):
        super(BreaksClosuresDayBtn, self).on_release()

        # Ignores action if button is a holiday
        if not self.__is_holiday:
            self.toggle_active()

            if self.__is_active:
                if callable(self.__activate_callback):
                    self.__activate_callback()
            else:
                if callable(self.__deactivate_callback):
                    self.__deactivate_callback()

        pass

    def toggle_active(self):
        if not self.__is_holiday:
            if self.__is_active:
                self.__is_active = False
                self.background_color = (0.9, 0.9, 0.9, 1)
            else:
                self.__is_active = True
                self.background_color = (0.6, 1, 0.6, 1)
