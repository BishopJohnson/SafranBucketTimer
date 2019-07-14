from define import *
from timer import Timer
from keypad import Keypad

import csv
from datetime import datetime
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from math import floor
from threading import Thread


def hours_minutes_seconds(seconds):
    hours = floor(seconds / SEC_PER_HOUR)
    seconds = seconds % SEC_PER_HOUR

    minutes = floor(seconds / SEC_PER_MIN)
    seconds = seconds % SEC_PER_MIN

    return hours, minutes, seconds


class MyWidget(FloatLayout):
    def __init__(self):
        super(MyWidget, self).__init__()
        self.keypad = None
        self.keypad_open = False

    def show_keypad(self, btn):
        if not self.keypad_open:
            self.keypad_open = True
            self.keypad = Keypad(btn)
            btn.add_widget(self.keypad)

    def hide_keypad(self):
        if self.keypad_open:
            self.keypad_open = False
            self.keypad.parent.remove_widget(self.keypad)
            self.keypad = None


class MyApp(App):
    def __init__(self):
        super(MyApp, self).__init__()
        self.buckets = list()
        self.bucket_running = False
        self.current_bucket = ''
        self.goal = 14760  # 14760 seconds is equal to 4.1 hours
        self.is_break = False
        self.is_running = True  # Boolean stating that the app is running
        self.named = False
        self.size = 0
        self.timer = Timer()
        self.times = list()
        self.__gui = None
        self.__thread_clock = None
        self.__thread_timer = None
        self.__time_end = None
        self.__time_start = None

    def append_bucket_name(self, digit):
        # Checks if the length is less than six
        if len(self.current_bucket) < 6:
            self.current_bucket += str(digit)

            # Updates the bucket name in the UI
            self.__gui.bkt_curr_name.text = 'CURRENT ({})'.format(self.current_bucket)

    def build(self):
        self.__gui = MyWidget()

        return self.__gui

    def cancel_bucket(self):
        # Check if a bucket is running
        if self.bucket_running:
            # Updates internal values
            self.bucket_running = False

            # Update button states
            self.__gui.start.disabled = False
            self.__gui.finish.disabled = True
            self.__gui.cancel.disabled = True

            # Joins the timer thread
            self.__thread_timer.join()

            self.__reset_bucket()

    def cancel_bucket_name(self):
        self.__gui.hide_keypad()
        self.__reset_bucket()

    def enter_bucket_name(self):
        # TODO: Call self.__check_bucket_name(). If function returns false, then ask if user wants to keep the name.
        if not self.__check_bucket_name():
            print('The bucket name was not found in the data file.')

        self.__gui.hide_keypad()
        self.start_bucket()

    def finish_bucket(self):
        # Check if a bucket is running
        if self.bucket_running:
            # Updates internal values
            self.bucket_running = False

            # Update button states
            self.__gui.start.disabled = False
            self.__gui.finish.disabled = True
            self.__gui.cancel.disabled = True

            # Joins the timer thread
            # self.__thread_timer.join()

            self.__time_end = datetime.now()

            # Updates table
            self.__update_table(self.current_bucket, self.timer.get_time())

            # Logs the bucket statistics
            self.__log_times()

            self.__reset_bucket()

    def on_start(self):
        # TODO: Check if "Alpha Numberic Bucket Numbers.xlsx" is present and if not then display message.

        # Goal for time with hours, minutes, and seconds
        # (hours, minutes, seconds) = hours_minutes_seconds(self.goal)
        # self.__gui.bkt_goal_time.text = '{}:{}:{}'.format(hours, minutes, seconds)

        # Goal for time with only hours
        self.__gui.bkt_goal_time.text = '{:.2f} Hrs'.format(self.goal / SEC_PER_HOUR)

        # Set initial button states
        self.__gui.start.disabled = False
        self.__gui.finish.disabled = True
        self.__gui.cancel.disabled = True

        # self.__thread_clock = Thread(target=self.__clock)
        # self.__thread_clock.start()

        # TODO: Schedule clock here.
        self.__clock_event = Clock.schedule_interval(self.update, 0)

    def on_stop(self):
        self.is_running = False

        # Joins the clock thread
        # self.__thread_clock.join()

        # TODO: Unschedule clock here.
        self.__clock_event.cancel()

    def start_bucket(self):
        # Checks if a bucket is already running
        if not self.bucket_running:
            # Updates internal values
            self.bucket_running = True

            # Update button states
            self.__gui.start.disabled = True
            self.__gui.finish.disabled = False
            self.__gui.cancel.disabled = False

            # Creates a thread for the timer
            # self.__thread_timer = Thread(target=self.__bucket_timer)
            # self.__thread_timer.start()

            self.timer.start()
            self.__time_start = datetime.now()

    def update(self, dt):
        if self.bucket_running:
            # Checks if a break is scheduled
            if True:#not self.is_break:
                # Method for time keeping with hours, minutes, and seconds
                (hours, minutes, seconds) = hours_minutes_seconds(self.timer.current())
                self.__gui.bkt_curr_time.text = '{}:{}:{}'.format(hours, minutes, seconds)

                # Method for time keeping with only hours
                # self.__gui.bkt_curr_time.text = '{:.2f} Hrs'.format(self.timer.current() / SEC_PER_HOUR)

        # Handles the clock
        self.__scheduled_break()  # Run function for breaks

        now = datetime.now()

        year = now.year
        month = now.month
        day = now.day
        hour = now.hour
        minute = now.minute
        second = now.second
        period = 'AM'  # Assume AM

        # Checks the period of the day
        if hour == 0:
            hour = 12
        elif hour >= 12:
            period = 'PM'

            # Checks if hour needs to recycle
            if hour > 12:
                hour = hour % 12

        self.__gui.clock.text = '{:02d}:{:02d}:{:02d} {:s}    {:02d}/{:02d}/{:d}'.format(hour,
                                                                                         minute,
                                                                                         second,
                                                                                         period,
                                                                                         month,
                                                                                         day,
                                                                                         year)

    def __pause_break(self):
        self.is_break = True
        self.__gui.pause_text.text = BREAK_TEXT

    def __bucket_timer(self):
        self.timer.start()

        while self.bucket_running:
            # Checks if a break is scheduled
            if not self.is_break:
                # Method for time keeping with hours, minutes, and seconds
                # (hours, minutes, seconds) = hours_minutes_seconds(self.timer.current())
                # self.__gui.bkt_curr_time.text = '{}:{}:{}'.format(hours, minutes, seconds)

                # Method for time keeping with only hours
                self.__gui.bkt_curr_time.text = '{:.2f} Hrs'.format(self.timer.current() / SEC_PER_HOUR)

    def __check_bucket_name(self):
        with open(DATA_FILE, newline='') as data_file:
            reader = csv.reader(data_file, delimiter=',')

            # Iterates for each row in the data file
            for row in reader:
                # Checks if the bucket name exists in the data file
                if row[0] == self.current_bucket:
                    return True

        return False

    def __clock(self):
        # Runs until the program shuts down
        while self.is_running:
            self.__scheduled_break()  # Run function for breaks

            now = datetime.now()

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

            self.__gui.clock.text = '{:02d}:{:02d} {:s}    {:02d}/{:02d}/{:d}'.format(hour,
                                                                                      minute,
                                                                                      period,
                                                                                      month,
                                                                                      day,
                                                                                      year)

    def __log_times(self):
        from pathlib import Path

        flag = 'a'  # Assume file will be appended to

        # Checks if the file does not exist
        if not Path(LOG_NAME).exists():
            flag = 'w'

        with open(LOG_NAME, flag, newline='') as log:
            writer = csv.writer(log, delimiter=',')

            # Checks if header row needs to be created
            if flag == 'w':
                writer.writerow(['bucket_number', 'work_time', 'start_date', 'end_date'])

            writer.writerow([self.current_bucket,
                             '{:.2f} Hrs'.format(self.timer.get_time() / SEC_PER_HOUR),
                             self.__time_start,
                             self.__time_end])

    def __reset_bucket(self):
        # Reverts to default state
        self.current_bucket = ''
        self.__gui.bkt_curr_name.text = 'CURRENT ()'
        self.__gui.bkt_curr_time.text = '0.00 Hrs'

    def __scheduled_break(self):
        from datetime import date

        now = datetime.now()  # Gets the current month, day, hour, and minute to determine
        month = now.month     # if a break should take place, based on work schedules or
        day = now.day         # factory holidays.
        hour = now.hour       #
        minute = now.minute   #
        today = date.today()           # Gets the day of the week as an integer
        weekday = date.weekday(today)  # where Monday == 0 and Sunday == 6.

        # Holidays
        if month == 7 and day == 4:  # 4th of July
            self.__pause_break()
        elif month == 12 and day in range(24, 26):  # Christmas Eve and Christmas
            self.__pause_break()
        else:  # Normal workdays
            if weekday in range(0, 4):  # Monday - Thursday
                if hour == 7 and minute in range(0, 15):  # (7:00 am) 15 min break
                    self.__pause_break()
                elif hour == 9 and minute in range(0, 30):  # (9:00 am) 30 min break
                    self.__pause_break()
                elif hour == 11 and minute in range(30, 45):  # (11:30 am) 15 min break
                    self.__pause_break()
                elif hour == 13 and minute in range(30, 40):  # (1:30 pm) 10 min break
                    self.__pause_break()
                elif hour == 17 and minute in range(45, 60):  # (5:45 pm) 15 min break
                    self.__pause_break()
                elif (hour == 19 and minute in range(45, 60)) or (hour == 20 and minute in range(0, 15)):  # (7:45 pm) 30 min break
                    self.__pause_break()
                elif hour == 22 and minute in range(15, 30):  # (10:15 pm) 15 min break
                    self.__pause_break()
                elif hour == 0 and minute in range(15, 25):  # (12:15 am) 10 min break
                    self.__pause_break()
                elif hour == 15 and minute in range(30, 45):  # End of day shift
                    self.__pause_break()
                elif weekday == 0 and hour in range(0, 5):  # No morning swing shift (Monday)
                    self.__pause_break()
                elif (hour == 2 and minute in range(15, 60)) or hour in range(3, 5):  # End of swing shift (Tuesday - Thursday)
                    self.__pause_break()
                else:  # No break
                    # Checks if a break has just ended
                    if self.is_break:
                        self.timer.reset()
                        self.__gui.pause_text.text = ''

                    self.is_break = False
            elif weekday == 4:  # Friday
                if hour == 7 and minute in range(0, 15):  # (7:00 am) 15 min break
                    self.__pause_break()
                elif hour == 9 and minute in range(0, 30):  # (9:00 am) 30 min break
                    self.__pause_break()
                elif hour == 11 and minute in range(30, 45):  # (11:30 am) 15 min break
                    self.__pause_break()
                elif hour == 16 and minute in range(0, 15):  # (4:00 pm) 15 min break
                    self.__pause_break()
                elif hour == 18 and minute in range(0, 30):  # (6:00 pm) 30 min break
                    self.__pause_break()
                elif hour == 20 and minute in range(0, 15):  # (8:00 pm) 15 min break
                    self.__pause_break()
                elif hour == 13 and minute in range(30, 60):  # End of day shift
                    self.__pause_break()
                elif (hour == 22 and minute in range(30, 60)) or hour == 23:  # End of swing shift
                    self.__pause_break()
                else:  # No break
                    # Checks if a break has just ended
                    if self.is_break:
                        self.timer.reset()
                        self.__gui.pause_text.text = ''

                    self.is_break = False
            else:  # Pause on weekends
                self.__pause_break()

    def __update_table(self, name, time):
        # Checks if the table is not full
        if self.size < 5:
            self.size += 1  # Increments size
        else:
            self.buckets.pop(4)  # Removes elements at the
            self.times.pop(4)    # end of the lists.

        self.buckets.insert(0, name)  # Inserts elements at the
        self.times.insert(0, time)    # front of the lists.

        # Precompiles the labels into parallel arrays
        gui = self.__gui
        labels_bkt = [gui.bucket_1, gui.bucket_2, gui.bucket_3, gui.bucket_4, gui.bucket_5]
        labels_time = [gui.time_1, gui.time_2, gui.time_3, gui.time_4, gui.time_5]

        # Variables used to calculate average time
        count = 0
        time_sum = 0

        # Iterates for each row in the table
        for i in range(0, 5):
            # Checks if the row has an entry
            if i < self.size:
                name = self.buckets[i]
                time = self.times[i]
                count += 1
                time_sum += time
            else:
                name = ''
                time = 0

            # Updates table UI
            labels_bkt[4 - i].text = str(name)
            labels_time[4 - i].text = '{:.2f} Hrs'.format(time / SEC_PER_HOUR)

        if count > 0:
            gui.time_avg.text = '{:.2f} Hrs'.format((time_sum / count) / SEC_PER_HOUR)


def main():
    MyApp().run()


if __name__ == '__main__':
    main()
