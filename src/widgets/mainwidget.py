# Custom packages
from src.define import hours_minutes_seconds
from src.define import Views
from src.define import SEC_PER_HOUR
from src.widgets.appwidget import AppWidget
from src.widgets.keypad import Keypad

from functools import partial
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout


Builder.load_file('src/kv/mainwidget.kv')


class MainWidget(FloatLayout, AppWidget):
    def __init__(self, app):
        super(MainWidget, self).__init__()

        self.__app = app
        self.__keypad = None
        self.__keypad_open = False

        self.cancel_btn.bind(on_release=self.__app.cancel_bucket)
        self.finish_btn.bind(on_release=self.__app.finish_bucket)
        self.options_btn.bind(on_release=partial(self.__app.gui.open_view, Views.OPTIONS_MENU))
        self.start_btn.bind(on_release=partial(self.show_keypad, self.start_btn))

    def hide_keypad(self, *args, **kwargs):
        if self.__keypad_open:
            self.__keypad_open = False
            self.__keypad.parent.remove_widget(self.__keypad)
            self.__keypad = None

    def hide_no_assigned_break_text(self):
        self.no_assigned_break_text.color = (1, 0, 0, 0)

    def hide_pause_text(self):
        self.pause_text.color = (1, 0, 0, 0)

    def notify(self):
        super(MainWidget, self).notify()

        # Updates the bucket name in the UI
        if self.__app.current_bucket_name == '':
            self.bkt_curr_name.text = 'CURRENT ()'
            self.bkt_curr_time.text = '0.00 Hrs'
        else:
            self.bkt_curr_name.text = 'CURRENT ({})'.format(self.__app.current_bucket_name)

        self.bkt_goal_time.text = '{:.2f} Hrs'.format(self.__app.goal / SEC_PER_HOUR)

        self.__update_buttons()
        self.__update_table()

        pass

    def show_keypad(self, btn, *args, **kwargs):
        if not self.__keypad_open:
            self.__keypad_open = True
            self.__keypad = Keypad(btn,
                                   num_callback=self.__app.append_bucket_name,
                                   enter_callback=self._keypad_enter_callback,
                                   cancel_callback=self._keypad_cancel_callback)

            btn.add_widget(self.__keypad)

    def show_no_assigned_break_text(self):
        self.no_assigned_break_text.color = (1, 0, 0, 1)

    def show_pause_text(self):
        self.pause_text.color = (1, 0, 0, 1)

    def update(self):
        super(MainWidget, self).update()

        if self.__app.is_bucket_running:
            # Time keeping with hours, minutes, and seconds
            # (hours, minutes, seconds) = hours_minutes_seconds(self.__app.clock.timer)
            # self.bkt_curr_time.text = f'{hours}:{minutes}:{seconds}'

            # Time keeping with only hours
            time = self.__app.clock.timer / SEC_PER_HOUR
            self.bkt_curr_time.text = f'{time:.2f} Hrs'

        # Handles the clock ui
        now = self.__app.clock.time

        year = now.year
        month = now.month
        day = now.day
        hour = now.hour
        minute = now.minute
        period = 'AM'  # Assume AM

        # Checks the period of the day
        if hour == 0:
            hour = 12
        elif hour >= 12:
            period = 'PM'

            # Checks if hour needs to recycle
            if hour > 12:
                hour = hour % 12

        self.clock.text = f'{hour:02d}:{minute:02d} {period:s}    {month:02d}/{day:02d}/{year:d}'

        if self.__app.clock.has_break():
            self.hide_no_assigned_break_text()

            if self.__app.clock.is_break_time():
                self.show_pause_text()
            else:
                self.hide_pause_text()
        else:
            self.hide_pause_text()
            self.show_no_assigned_break_text()

    def _keypad_cancel_callback(self, *args, **kwargs):
        self.__app.cancel_bucket_name()
        self.hide_keypad()

    def _keypad_enter_callback(self, *args, **kwargs):
        self.__app.enter_bucket_name()
        self.hide_keypad()

    def __update_buttons(self):
        if self.__app.is_bucket_running:
            self.start_btn.disabled = True
            self.finish_btn.disabled = False
            self.cancel_btn.disabled = False
        else:
            self.start_btn.disabled = False
            self.finish_btn.disabled = True
            self.cancel_btn.disabled = True

    def __update_table(self):
        buckets = self.__app.buckets
        times = self.__app.times
        labels_bkt = [self.bucket_1, self.bucket_2, self.bucket_3, self.bucket_4, self.bucket_5]
        labels_time = [self.time_1, self.time_2, self.time_3, self.time_4, self.time_5]

        count = 0
        time_sum = 0

        for i in range(0, self.__app.max_size):
            if i < self.__app.size:
                name = buckets[i]
                time = times[i]
                count += 1
                time_sum += time
            else:
                name = ''
                time = 0

            # Updates table UI
            labels_bkt[4 - i].text = str(name)
            labels_time[4 - i].text = '{:.2f} Hrs'.format(time / SEC_PER_HOUR)

        if count > 0:
            self.time_avg.text = '{:.2f} Hrs'.format((time_sum / count) / SEC_PER_HOUR)
