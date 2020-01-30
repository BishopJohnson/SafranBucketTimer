# Custom packages
from src.clock import Clock as Clk
from src.define import *
from src.fileprocessing import *
from src.widgets.popup import NameWarning
from src.widgets.rootwidget import RootWidget
from src.workbreak import WorkBreak

import csv
from datetime import datetime, timedelta
from kivy.app import App
from kivy.clock import Clock as ClkEvent
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


class MyApp(App):
    def __init__(self):
        super(MyApp, self).__init__()
        self.__brk_list = list()
        self.__buckets = list()
        self.__clock = Clk()
        self.__clock_event = None
        self.__current_bucket_name = ''
        self.__goal = 14760  # 14760 seconds is equal to 4.1 hours
        self.__gui = None
        self.__is_bucket_running = False
        self.__max_size = 5
        self.__size = 0
        self.__times = list()

    @property
    def buckets(self):
        return self.__buckets.copy()

    @property
    def clock(self):
        return self.__clock

    @property
    def current_bucket_name(self):
        return self.__current_bucket_name

    @property
    def goal(self):
        return self.__goal

    @property
    def is_bucket_running(self):
        return self.__is_bucket_running

    @property
    def max_size(self):
        return self.__max_size

    @property
    def size(self):
        return self.__size

    @property
    def times(self):
        return self.__times.copy()

    def append_bucket_name(self, digit, *args, **kwargs):
        # Checks if the name length is less than six
        if len(self.__current_bucket_name) < 6:
            self.__current_bucket_name += str(digit)

            self.__gui.notify()

    def build(self):
        super(MyApp, self).build()

        self.__gui = RootWidget(self)
        self.open_view(MAIN_VIEW)

        return self.__gui

    def cancel_bucket(self, *args, **kwargs):
        if self.__is_bucket_running:
            self.__is_bucket_running = False
            self.__clock.stop_timer()
            self.__reset_bucket()

            self.__gui.notify()

    def cancel_bucket_name(self, *args, **kwargs):
        self.__reset_bucket()

    def enter_bucket_name(self, *args, **kwargs):
        # Checks if the bucket name exists in the names file
        if not self.__check_bucket_name():
            NameWarning(self).open()  # Opens a popup menu
        else:
            self.start_bucket()

    def finish_bucket(self, *args, **kwargs):
        if self.__is_bucket_running:
            self.__is_bucket_running = False
            self.__clock.stop_timer()

            # Updates table
            self.__update_table(self.__current_bucket_name, self.__clock.timer_time())

            # Logs the bucket statistics
            self.__log_times()

            self.__reset_bucket()

            self.__gui.notify()

    def on_start(self):
        super(MyApp, self).on_start()

        # TODO: Check if name file is present and if not then display a message.

        # Populates work break list and assigns a break to the clock
        self.__brk_list = create_break_list()
        self.__assign_break()

        # Set the bucket and time lists as lists of past data
        self.__recent_buckets()

        # Schedule the clock event
        self.__clock_event = ClkEvent.schedule_interval(self.update, 0)

        self.__gui.notify()

    def on_stop(self):
        super(MyApp, self).on_stop()

        # Unschedule the clock event
        self.__clock_event.cancel()

    def open_view(self, view, *args, **kwargs):
        if view == MAIN_VIEW:
            self.__gui.show_main()
        elif view == OPTIONS_VIEW:
            self.__gui.show_options()
        else:
            print('No such view {}'.format(view))

    def start_bucket(self, *args, **kwargs):
        if not self.__is_bucket_running:
            self.__is_bucket_running = True
            self.__clock.start_timer()

            self.__gui.notify()

    def update(self, dt):
        self.__clock.update()
        self.__gui.update()

    def __assign_break(self):
        # Checks if the list is empty
        if len(self.__brk_list) == 0:
            self.__brk_list = create_break_list()

        # Check if the list is still empty
        if len(self.__brk_list) > 0:
            brk = self.__brk_list.pop(0)  # Pop the front-most break
            self.__clock.assign_break(brk, self.__assign_break)

    def __check_bucket_name(self):
        try:
            with open(NAMES_FILE, newline='') as data_file:
                reader = csv.reader(data_file, delimiter=',')

                # Iterates for each row in the data file
                for row in reader:
                    # Checks if the bucket name exists in the data file
                    if row[0] == self.__current_bucket_name:
                        return True
        except FileNotFoundError:
            return True  # Return true if the file cannot be found

        return False  # Return false if the bucket name was not found

    def __log_times(self):
        # Create the log file if it does not exist
        create_log_file()

        with open(LOG_FILE, 'a', newline='') as log:
            writer = csv.writer(log, delimiter=',')

            writer.writerow([self.__current_bucket_name,
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
        self.__current_bucket_name = ''

        self.__gui.notify()

    def __update_table(self, name, time):
        # Checks if the table is not full
        if self.__size < self.__max_size:
            self.__size += 1
        else:
            self.__buckets.pop(self.__max_size - 1)  # Removes elements at the
            self.__times.pop(self.__max_size - 1)    # end of the lists.

        self.__buckets.insert(0, name)  # Inserts elements at the
        self.__times.insert(0, time)    # front of the lists.

        self.__gui.notify()
