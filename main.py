# Custom packages
from define import *
from fileprocessing import *
from clock import Clock as Clk
from keypad import Keypad
from popup import NameWarning
from workbreak import WorkBreak

import csv
from datetime import datetime, timedelta
from kivy.app import App
from kivy.clock import Clock as ClkEvent
from kivy.uix.floatlayout import FloatLayout
from math import floor
from operator import attrgetter


def create_break_list(days=14):
    data = import_data_file()
    brk_list = list()
    dt = datetime.now()

    # Instantiates all of the scheduled breaks for the next few days specified
    for i in range(0, days):
        current = datetime(year=dt.year, month=dt.month, day=dt.day) + timedelta(days=i)

        # Iterates over each break
        for brk in data['breaks']:
            # Checks if the break occurs on the current day
            if brk['weekday'] == current.weekday():
                start = current + timedelta(hours=brk['start_hour'], minutes=brk['start_minute'])
                end = current + timedelta(hours=brk['end_hour'], minutes=brk['end_minute'])

                try:
                    brk_list.append(WorkBreak(start, end))
                except TypeError:
                    print('Error assigning work break!')

    # Sorts the list so that breaks that occur sooner are at the front
    return sorted(brk_list, key=attrgetter('start'))


def hours_minutes_seconds(seconds):
    hours = floor(seconds / SEC_PER_HOUR)
    seconds = seconds % SEC_PER_HOUR

    minutes = floor(seconds / SEC_PER_MIN)
    seconds = seconds % SEC_PER_MIN

    return hours, minutes, seconds


def intersect_breaks(first, second):
    if first['weekday'] == second['weekday']:
        first_start = first['start_hour'] * MIN_PER_HOUR + first['start_minute']
        first_end = first['end_hour'] * MIN_PER_HOUR + first['end_minute']
        second_start = second['start_hour'] * MIN_PER_HOUR + second['start_minute']
        second_end = second['end_hour'] * MIN_PER_HOUR + second['end_minute']

        # Checks if an intersections occur
        if first_start <= second_start and first_end >= second_end:  # The second is a subset of the first
            return True
        elif first_start > second_start and first_end < second_end:  # The first is a subset of the second
            return True
        elif first_start <= second_start <= first_end:  # The second starts within the first
            return True
        elif first_start <= second_end <= first_end:  # The second ends within the first
            return True

    return False


def join_breaks(first, second):
    result = None

    if intersect_breaks(first, second):
        # Sets start hour and minute to the sooner break
        if first['start_hour'] < second['start_hour']:
            start_hour = first['start_hour']
            start_minute = first['start_minute']
        elif first['start_hour'] > second['start_hour']:
            start_hour = second['start_hour']
            start_minute = second['start_minute']
        else:
            start_hour = first['start_hour']

            if first['start_minute'] < second['start_minute']:
                start_minute = first['start_minute']
            else:
                start_minute = second['start_minute']

        # Sets end hour and minute to the later break
        if first['end_hour'] > second['end_hour']:
            end_hour = first['end_hour']
            end_minute = first['end_minute']
        elif first['end_hour'] < second['end_hour']:
            end_hour = second['end_hour']
            end_minute = second['end_minute']
        else:
            end_hour = first['end_hour']

            if first['end_minute'] > second['end_minute']:
                end_minute = first['end_minute']
            else:
                end_minute = second['end_minute']

        result = {
            'weekday': first['weekday'],
            'start_hour': start_hour,
            'start_minute': start_minute,
            'end_hour': end_hour,
            'end_minute': end_minute
        }

    return result


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

    def show_no_assigned_break_text(self):
        self.no_assigned_break_text.color = (1, 0, 0, 1)

    def show_pause_text(self):
        self.pause_text.color = (1, 0, 0, 1)

    def hide_keypad(self):
        if self.keypad_open:
            self.keypad_open = False
            self.keypad.parent.remove_widget(self.keypad)
            self.keypad = None

    def hide_no_assigned_break_text(self):
        self.no_assigned_break_text.color = (1, 0, 0, 0)

    def hide_pause_text(self):
        self.pause_text.color = (1, 0, 0, 0)


class MyApp(App):
    def __init__(self):
        super(MyApp, self).__init__()
        self.__brk_list = list()
        self.__bucket_running = False
        self.__buckets = list()
        self.__clock = Clk()
        self.__clock_event = None
        self.__current_bucket = ''
        self.__goal = 14760  # 14760 seconds is equal to 4.1 hours
        self.__gui = None
        self.__max_size = 5
        self.__size = 0
        self.__times = list()

    def append_bucket_name(self, digit):
        # Checks if the name length is less than six
        if len(self.__current_bucket) < 6:
            self.__current_bucket += str(digit)

            # Updates the bucket name in the UI
            self.__gui.bkt_curr_name.text = 'CURRENT ({})'.format(self.__current_bucket)

    def build(self):
        self.__gui = MyWidget()

        return self.__gui

    def cancel_bucket(self):
        # Check if a bucket is running
        if self.__bucket_running:
            self.__bucket_running = False
            self.__clock.stop_timer()

            # Update button states
            self.__gui.start_btn.disabled = False
            self.__gui.finish_btn.disabled = True
            self.__gui.cancel_btn.disabled = True

            self.__reset_bucket()

    def cancel_bucket_name(self):
        self.__gui.hide_keypad()
        self.__reset_bucket()

    def enter_bucket_name(self):
        self.__gui.hide_keypad()

        # Checks if the bucket name exists in the names file
        if not self.__check_bucket_name():
            NameWarning(self).open()  # Opens a popup menu
        else:
            self.start_bucket()

    def finish_bucket(self):
        # Check if a bucket is running
        if self.__bucket_running:
            self.__bucket_running = False
            self.__clock.stop_timer()

            # Update button states
            self.__gui.start_btn.disabled = False
            self.__gui.finish_btn.disabled = True
            self.__gui.cancel_btn.disabled = True

            # Updates table
            self.__update_table(self.__current_bucket, self.__clock.timer_time())

            # Logs the bucket statistics
            self.__log_times()

            self.__reset_bucket()

    def on_start(self):
        # TODO: Check if name file is present and if not then display a message.

        # Populates work break list and assigns a break to the clock
        self.__brk_list = create_break_list()
        self.__assign_break()

        # Set the bucket and time lists as lists of past data
        self.__recent_buckets()

        # Goal for time with only hours
        self.__gui.bkt_goal_time.text = '{:.2f} Hrs'.format(self.__goal / SEC_PER_HOUR)

        # Set initial button states
        self.__gui.start_btn.disabled = False
        self.__gui.finish_btn.disabled = True
        self.__gui.cancel_btn.disabled = True

        # Schedule the clock event
        self.__clock_event = ClkEvent.schedule_interval(self.update, 0)

    def on_stop(self):
        # Unschedule the clock event
        self.__clock_event.cancel()

    def start_bucket(self):
        # Checks if a bucket is already running
        if not self.__bucket_running:
            self.__bucket_running = True
            self.__clock.start_timer()

            # Update button states
            self.__gui.start_btn.disabled = True
            self.__gui.finish_btn.disabled = False
            self.__gui.cancel_btn.disabled = False

    def update(self, dt):
        self.__clock.update()

        # Handles the bucket timer
        if self.__bucket_running:

            # Time keeping with hours, minutes, and seconds
            # (hours, minutes, seconds) = hours_minutes_seconds(self.__clock.timer_time())
            # self.__gui.bkt_curr_time.text = '{}:{}:{}'.format(hours, minutes, seconds)

            # Time keeping with only hours
            self.__gui.bkt_curr_time.text = '{:.2f} Hrs'.format(self.__clock.timer_time() / SEC_PER_HOUR)

        # Handles the clock ui
        now = self.__clock.time()

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

        if self.__clock.is_break_time():
            self.__gui.show_pause_text()
        else:
            self.__gui.hide_pause_text()

    def __assign_break(self):
        # Checks if the list is empty
        if len(self.__brk_list) == 0:
            self.__brk_list = create_break_list()

        # Check if the list is still empty
        if len(self.__brk_list) == 0:
            self.__gui.show_no_assigned_break_text()
        else:
            brk = self.__brk_list.pop(0)  # Pop the front-most break
            self.__clock.assign_break(brk, self.__assign_break)
            self.__gui.hide_no_assigned_break_text()

    def __check_bucket_name(self):
        try:
            with open(NAMES_FILE, newline='') as data_file:
                reader = csv.reader(data_file, delimiter=',')

                # Iterates for each row in the data file
                for row in reader:
                    # Checks if the bucket name exists in the data file
                    if row[0] == self.__current_bucket:
                        return True
        except FileNotFoundError:
            return True  # Return true if the file cannot be found

        return False  # Return false if the bucket name was not found

    def __log_times(self):
        # Create the log file if it does not exist
        create_log_file()

        with open(LOG_FILE, 'a', newline='') as log:
            writer = csv.writer(log, delimiter=',')

            writer.writerow([self.__current_bucket,
                             '{:.2f} Hrs'.format(self.__clock.timer_time() / SEC_PER_HOUR),
                             self.__clock.timer_time(),
                             self.__clock.timer_start_time(),
                             self.__clock.timer_end_time()])

    def __recent_buckets(self):
        count = 0
        buckets = list()
        times = list()

        try:
            with open(LOG_FILE, newline='') as data_file:
                reader = csv.reader(data_file, delimiter=',')

                next(reader)  # Skips the headers

                # Gets the bucket names and times (sec)
                for row in reader:
                    buckets.append(row[0])
                    times.append(row[2])
                    count += 1
        except FileNotFoundError:
            print("No log file to get recent bucket times from.")

            # Create the log file if it does not exist
            create_log_file()
        finally:
            # Iterates over the last few desired entries and adds them to the table
            i = max(0, count - self.__max_size)
            while i < count:
                self.__update_table(str(buckets[i]), int(times[i]))
                i += 1

    def __reset_bucket(self):
        # Reverts to default state
        self.__current_bucket = ''
        self.__gui.bkt_curr_name.text = 'CURRENT ()'
        self.__gui.bkt_curr_time.text = '0.00 Hrs'

    def __update_table(self, name, time):
        # Checks if the table is not full
        if self.__size < self.__max_size:
            self.__size += 1
        else:
            self.__buckets.pop(self.__max_size - 1)  # Removes elements at the
            self.__times.pop(self.__max_size - 1)    # end of the lists.

        self.__buckets.insert(0, name)  # Inserts elements at the
        self.__times.insert(0, time)    # front of the lists.

        # Precompiles the labels into parallel arrays
        gui = self.__gui
        labels_bkt = [gui.bucket_1, gui.bucket_2, gui.bucket_3, gui.bucket_4, gui.bucket_5]
        labels_time = [gui.time_1, gui.time_2, gui.time_3, gui.time_4, gui.time_5]

        # Variables used to calculate average time
        count = 0
        time_sum = 0

        # Iterates for each row in the table
        for i in range(0, self.__max_size):
            # Checks if the row has an entry
            if i < self.__size:
                name = self.__buckets[i]
                time = self.__times[i]
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
