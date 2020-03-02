# Custom packages
from src.define import hours_minutes_seconds
from src.define import Views
from src.define import SEC_PER_HOUR
from src.timer import Timer
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

    def hide_closure_text(self):
        self.closure_text.color = (1, 0, 0, 0)

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

        # Updates UI elements reliant on config data
        config = self.__app.config_cache
        goal_time = config['goal_time']
        team_name = config['team_name']

        # Tries to format the goal time if it's a float
        try:
            self.bkt_goal_time.text = f'{float(goal_time):.02f} Hrs'
        except ValueError:
            self.bkt_goal_time.text = f'{goal_time} Hrs'

        # Appends 's if team name was set
        if len(team_name) > 0:
            team_name = f'{team_name}\'s '

        self.team_label.text = f'{team_name.upper()}BUCKET TIME TRACKER'

        self.__update_buttons()
        self.__update_current_buckets()
        self.__update_table()

        pass

    def show_closure_text(self):
        self.closure_text.color = (1, 0, 0, 1)

    def show_keypad(self, btn, *args, **kwargs):
        if not self.__keypad_open:
            self.__keypad_open = True
            self.__keypad = Keypad(btn,
                                   max_length=self.__app.max_name_length,
                                   enter_callback=self._keypad_enter_callback,
                                   cancel_callback=self.hide_keypad)

            btn.add_widget(self.__keypad)

    def show_no_assigned_break_text(self):
        self.no_assigned_break_text.color = (1, 0, 0, 1)

    def show_pause_text(self):
        self.pause_text.color = (1, 0, 0, 1)

    def update(self):
        super(MainWidget, self).update()

        if self.__app.is_bucket_running():
            bucket_one = self.__app.bucket_one
            bucket_two = self.__app.bucket_two

            if isinstance(bucket_one, Timer):
                # Time keeping with hours, minutes, and seconds
                # (hours, minutes, seconds) = hours_minutes_seconds(bucket_one.seconds)
                # self.bkt_one_time.text = f'{hours}:{minutes}:{seconds}'

                # Time keeping with only hours
                time = bucket_one.seconds / SEC_PER_HOUR
                self.bkt_one_time.text = f'{time:.2f} Hrs'

            if isinstance(bucket_two, Timer):
                # Time keeping with hours, minutes, and seconds
                # (hours, minutes, seconds) = hours_minutes_seconds(bucket_two.seconds)
                # self.bkt_two_time.text = f'{hours}:{minutes}:{seconds}'

                # Time keeping with only hours
                time = bucket_two.seconds / SEC_PER_HOUR
                self.bkt_two_time.text = f'{time:.2f} Hrs'

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

        # Handles closure and break texts
        if self.__app.clock.is_closure():
            self.show_closure_text()
            self.hide_no_assigned_break_text()
            self.hide_pause_text()
        else:
            self.hide_closure_text()

            if self.__app.clock.has_break():
                self.hide_no_assigned_break_text()

                if self.__app.clock.is_break_time():
                    self.show_pause_text()
                else:
                    self.hide_pause_text()
            else:
                self.hide_pause_text()
                self.show_no_assigned_break_text()

    def _keypad_enter_callback(self, *args, **kwargs):
        self.__app.enter_bucket_name(self.__keypad.num)
        self.hide_keypad()

    def __update_buttons(self):
        bucket_one = self.__app.bucket_one
        bucket_two = self.__app.bucket_two

        if bucket_one is None and bucket_two is None:  # Neither bucket is running
            self.start_btn.disabled = False
            self.finish_btn.disabled = True
            self.cancel_btn.disabled = True
        elif bucket_one is not None and bucket_two is not None:  # Both buckets are running
            self.start_btn.disabled = True
            self.finish_btn.disabled = False
            self.cancel_btn.disabled = False
        else:  # At least one bucket is running
            self.start_btn.disabled = False
            self.finish_btn.disabled = False
            self.cancel_btn.disabled = False

    def __update_current_buckets(self):
        bucket_one = self.__app.bucket_one
        bucket_two = self.__app.bucket_two
        max_name_length = self.__app.max_name_length

        if isinstance(bucket_one, Timer):
            if len(bucket_one.name) > max_name_length:
                text = 'PRIORITY 1\n{}...'.format(bucket_one.name[:max_name_length])
            else:
                text = 'PRIORITY 1\n{}'.format(bucket_one.name)

            self.bkt_one_name.text = text
        else:
            self.bkt_one_name.text = 'PRIORITY 1\n----'
            self.bkt_one_time.text = '0.00 Hrs'

        if isinstance(bucket_two, Timer):
            if len(bucket_two.name) > max_name_length:
                text = 'PRIORITY 2\n{}...'.format(bucket_two.name[:max_name_length])
            else:
                text = 'PRIORITY 2\n{}'.format(bucket_two.name)

            self.bkt_two_name.text = text
        else:
            self.bkt_two_name.text = 'PRIORITY 2\n----'
            self.bkt_two_time.text = '0.00 Hrs'

    def __update_table(self):
        n = 5  # TODO: Make N a config setting and allow labels_bkt and labels_time to scale to it.
        labels_bkt = [self.bucket_1, self.bucket_2, self.bucket_3, self.bucket_4, self.bucket_5]
        labels_time = [self.time_1, self.time_2, self.time_3, self.time_4, self.time_5]

        log = self.__app.log_cache[-n:]  # The last N buckets
        log.reverse()

        count = 0
        time_sum = 0

        for i in range(0, n):
            if i < len(log):
                bkt = log[i]
                name = str(bkt[0])
                time = int(bkt[2])

                if len(name) > self.__app.max_name_length:
                    name = '{}...'.format(name[:self.__app.max_name_length])

                count += 1
                time_sum += time
            else:
                name = ''
                time = 0

            # Updates table UI
            labels_bkt[4 - i].text = name
            labels_time[4 - i].text = '{:.2f} Hrs'.format(time / SEC_PER_HOUR)

        if count > 0:
            self.time_avg.text = '{:.2f} Hrs'.format((time_sum / count) / SEC_PER_HOUR)
