# Custom packages
from src.clock import Clock as Clk
from src.define import *
from src.fileprocessing import *
from src.widgets.popup import NameWarning
from src.widgets.rootwidget import RootWidget
from src.workbreak import WorkBreak

import csv
from datetime import date, datetime, timedelta
from kivy.app import App
from kivy.clock import Clock as ClkEvent
from operator import attrgetter


def break_ends_next_week(brk):
    for key in BREAK_KEYS:
        if key not in brk:
            raise KeyError('Missing work break key!')

    if brk['end_weekday'] < brk['start_weekday']:
        return True
    else:
        if brk['end_weekday'] == brk['start_weekday'] and brk['end_hour'] < brk['start_hour']:
            return True
        else:
            if brk['end_weekday'] == brk['start_weekday'] and brk['end_hour'] == brk['start_hour'] and brk['end_minute'] < brk['start_minute']:
                return True

    return False


def create_break_list(data, *args, days_before=14, days_after=14, remove_past_breaks=True, **kwargs):
    brk_list = list()
    dt = datetime.now()

    # Instantiates all of the scheduled breaks for the next few days specified
    for i in range(0, days_before + days_after):
        current = datetime(year=dt.year, month=dt.month, day=dt.day) + timedelta(days=i - days_before)

        for brk in data['breaks']:
            if brk['start_weekday'] == current.weekday():
                start_date = current + timedelta(hours=brk['start_hour'], minutes=brk['start_minute'])

                # Checks if the break ends the week after
                if break_ends_next_week(brk):
                    end_date = current + timedelta(days=7 + (brk['end_weekday'] - brk['start_weekday']),
                                                   hours=brk['end_hour'],
                                                   minutes=brk['end_minute'])
                else:
                    end_date = current + timedelta(days=brk['end_weekday'] - brk['start_weekday'],
                                                   hours=brk['end_hour'],
                                                   minutes=brk['end_minute'])

                brk_list.append(WorkBreak(start_date, end_date))

    # Sorts the list so that breaks that occur sooner are at the front
    brk_list = sorted(brk_list, key=attrgetter('start'))

    if remove_past_breaks:
        while len(brk_list) > 0 and brk_list[0].end < dt:
            brk_list.pop(0)

    return brk_list


def create_closure_list(data, *args, days_before=365, **kwargs):
    closure_list = list()

    for closure in data['closures']:
        closure_list.append(date(closure['year'], closure['month'], closure['day']))

    closure_list.sort()

    now = date.today()

    # Removes closures before the days before threshold
    while len(closure_list) > 0 and (now - closure_list[0]).days > days_before:
        closure_list.pop(0)

    return closure_list


def intersect_breaks(first, second):
    first = _construct_temp_break(first)
    second = _construct_temp_break(second)

    if first.start <= second.start <= first.end or first.start <= second.end <= first.end:  # Overlaps but no subsets
        return True
    elif first.start <= second.start and second.end <= first.end:  # Second is a subset of first
        return True
    elif second.start <= first.start and first.end <= second.end:  # First is a subset of second
        return True

    return False


def join_breaks(first, second):
    result = None

    if intersect_breaks(first, second):
        first_brk = _construct_temp_break(first)
        second_brk = _construct_temp_break(second)

        if first_brk.start <= second_brk.start:
            start = first
        else:
            start = second

        if first_brk.end >= second_brk.end:
            end = first
        else:
            end = second

        result = {
            'start_weekday': start['start_weekday'],
            'start_hour': start['start_hour'],
            'start_minute': start['start_minute'],
            'end_weekday': end['end_weekday'],
            'end_hour': end['end_hour'],
            'end_minute': end['end_minute']
        }

    return result


def _construct_temp_break(brk):
    for key in BREAK_KEYS:
        if key not in brk:
            raise KeyError('Missing work break key!')

    current = datetime(year=2000, month=1, day=1)

    # Increments the day until the weekdays are the same
    count = 0
    while current.weekday() != brk['start_weekday']:
        current += timedelta(days=1)
        count += 1

        # Raises error if a full week passes
        if count > Days.SUNDAY.value:
            raise RuntimeError

    start_date = current + timedelta(hours=brk['start_hour'], minutes=brk['start_minute'])

    # Checks if the break ends the week after
    if break_ends_next_week(brk):
        end_date = current + timedelta(days=7 + (brk['end_weekday'] - brk['start_weekday']),
                                       hours=brk['end_hour'],
                                       minutes=brk['end_minute'])
    else:
        end_date = current + timedelta(days=brk['end_weekday'] - brk['start_weekday'],
                                       hours=brk['end_hour'],
                                       minutes=brk['end_minute'])

    return WorkBreak(start_date, end_date)


class MyApp(App):
    def __init__(self):
        super(MyApp, self).__init__()
        self.__brk_list = list()
        self.__clock = Clk()
        self.__clock_event = None
        self.__closure_list = list()
        self.__current_bucket_name = ''
        self.__config_cache = None
        self.__data_cache = None
        self.__gui = None
        self.__is_bucket_running = False
        self.__log_cache = None

    @property
    def clock(self):
        return self.__clock

    @property
    def config_cache(self):
        return self.__config_cache.copy()

    @property
    def current_bucket_name(self):
        return self.__current_bucket_name

    @property
    def data_cache(self):
        return self.__data_cache.copy()

    @property
    def is_bucket_running(self):
        return self.__is_bucket_running

    @property
    def gui(self):
        return self.__gui

    @property
    def log_cache(self):
        return self.__log_cache.copy()

    def add_break(self, brk, *args, **kwargs):
        for key in BREAK_KEYS:
            if key not in brk:
                return False

        # Checks if the break overlaps with an existing break and joins them if true
        for current_brk in self.__data_cache['breaks']:
            joined_brk = join_breaks(current_brk, brk)  # Attempt to join the breaks

            if joined_brk is not None:
                self.__data_cache['breaks'].remove(current_brk)

                return self.add_break(joined_brk)  # Recursive call to add the joined break

        if self.__is_bucket_running:
            self.__update_bucket_saved_data()

        self.__data_cache['breaks'].append(brk)
        write_data_file(self.__data_cache)

        # Recreates the break list with the new break
        self.__brk_list = create_break_list(self.__data_cache)
        self.__assign_break()

        self.__gui.notify()

        return True

    def add_closure(self, closure, *args, **kwargs):
        for key in CLOSURE_KEYS:
            if key not in closure:
                return False

        # Checks if the closure already exists in the data array
        for current_closure in self.__data_cache['closures']:
            if current_closure == closure:
                return False

        if self.__is_bucket_running:
            self.__update_bucket_saved_data()

        self.__data_cache['closures'].append(closure)
        write_data_file(self.__data_cache)

        # Recreates the closure list with the new closure
        self.__closure_list = create_closure_list(self.__data_cache)
        self.__assign_closure()

        self.__gui.notify()

        return True

    def append_bucket_name(self, digit, *args, **kwargs):
        # Checks if the name length is less than six
        if len(self.__current_bucket_name) < 6:
            self.__current_bucket_name += str(digit)

            self.__gui.notify()

    def build(self):
        super(MyApp, self).build()

        self.__config_cache = import_config_file()
        self.__data_cache = import_data_file()
        self.__log_cache = import_log_file()

        self.__gui = RootWidget(self)
        self.__gui.open_view(Views.MAIN)

        return self.__gui

    def cancel_bucket(self, *args, **kwargs):
        if self.__is_bucket_running:
            self.__is_bucket_running = False
            self.__clock.stop_timer()
            self.__clear_bucket_saved_data()
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

            # Logs the bucket statistics
            self.__log_times()

            self.__clear_bucket_saved_data()
            self.__reset_bucket()

            self.__gui.notify()

    def on_start(self):
        super(MyApp, self).on_start()

        # TODO: Check if name file is present and if not then display a message.

        # Populates work break list and assigns a break to the clock
        self.__brk_list = create_break_list(self.__data_cache)
        self.__closure_list = create_closure_list(self.__data_cache)
        self.__assign_break()
        self.__assign_closure()

        # Schedule the clock event
        self.__clock_event = ClkEvent.schedule_interval(self.update, 0)

        if self.__data_cache['bucket'] is not None:
            # TODO: Open popup to ask if user wants to resume the bucket.

            self.__resume_bucket()

        self.__gui.notify()

    def on_stop(self):
        super(MyApp, self).on_stop()

        # Unschedule the clock event
        self.__clock_event.cancel()

    def remove_break(self, brk, *args, **kwargs):
        for key in BREAK_KEYS:
            if key not in brk:
                return False

        if brk in self.__data_cache['breaks']:
            self.__data_cache['breaks'].remove(brk)
            write_data_file(self.__data_cache)

            if self.__is_bucket_running:
                self.__update_bucket_saved_data()

            # Recreates the break list without the removed break
            self.__brk_list = create_break_list(self.__data_cache)
            self.__assign_break()

            self.__gui.notify()

            return True

        return False

    def remove_closure(self, closure, *args, **kwargs):
        for key in CLOSURE_KEYS:
            if key not in closure:
                return False

        if closure in self.__data_cache['closures']:
            self.__data_cache['closures'].remove(closure)
            write_data_file(self.__data_cache)

            if self.__is_bucket_running:
                self.__update_bucket_saved_data()

            # Recreates the closure list without the removed closure
            self.__closure_list = create_closure_list(self.__data_cache)
            self.__assign_closure()

            self.__gui.notify()

            return True

        return False

    def start_bucket(self, *args, **kwargs):
        if not self.__is_bucket_running:
            self.__is_bucket_running = True
            self.__clock.start_timer()
            self.__update_bucket_saved_data()

            self.__gui.notify()

    def update(self, dt):
        self.__clock.update()
        self.__gui.update()

    def update_config(self, config, *args, **kwargs):
        for key in config:
            # Only pulls keys that are valid file keys
            if key in CONFIG_FILE_KEYS:
                self.__config_cache[key] = config[key]

        write_config_file(self.__config_cache)

        self.__gui.notify()

    def __assign_break(self):
        # Checks if the list is empty
        if len(self.__brk_list) == 0:
            self.__brk_list = create_break_list(self.__data_cache)

        # Check if the list is still empty
        if len(self.__brk_list) > 0:
            brk = self.__brk_list.pop(0)  # Pop the front-most break
            self.__clock.assign_break(brk, self.__assign_break)
        else:
            self.__clock.assign_break(None)

    def __assign_closure(self):
        # Checks if the list is empty
        if len(self.__closure_list) == 0:
            self.__closure_list = create_closure_list(self.__data_cache)

        # Check if the list is still empty
        if len(self.__closure_list) > 0:
            closure = self.__closure_list.pop(0)  # Pop the front-most closure
            self.__clock.assign_closure(closure, self.__assign_closure)
        else:
            self.__clock.assign_closure(None)

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

    def __clear_bucket_saved_data(self):
        self.__data_cache['bucket'] = None

        write_data_file(self.__data_cache)

    def __log_times(self):
        name = self.__current_bucket_name
        time = self.__clock.timer
        start_date = self.__clock.timer_start_time()
        end_date = self.__clock.timer_end_time()

        exp_date = self.__clock.time + timedelta(days=-7)  # Expiration date is seven day before now

        # Combines any recent buckets with this bucket
        i = 0
        while i < len(self.__log_cache):
            past_bkt = self.__log_cache[i]
            past_bkt_name = past_bkt[0]
            past_bkt_end = datetime.strptime(past_bkt[4], DATE_FORMAT)

            if past_bkt_name == name and past_bkt_end >= exp_date:
                time += int(past_bkt[2])

                # Checks if the logged start date is further in the past
                logged_start_date = datetime.strptime(past_bkt[3], DATE_FORMAT)
                if logged_start_date < start_date:
                    start_date = logged_start_date

                self.__log_cache.pop(i)
            else:
                i += 1

        self.__log_cache.append([
            name,
            '{:.2f} Hrs'.format(time / SEC_PER_HOUR),
            str(time),
            str(start_date),
            str(end_date)
        ])

        write_log_file(self.__log_cache)

        self.__gui.notify()

    def __reset_bucket(self):
        self.__current_bucket_name = ''

        self.__gui.notify()

    def __resume_bucket(self):
        bucket = self.__data_cache['bucket']

        if bucket is not None:
            # Formats the continuous date back to a datetime object
            cont_date = datetime.strptime(bucket['continuous_date'], DATE_FORMAT)

            # Creates list of all breaks between now and when the bucket was assigned to the current breaks set
            now = self.__clock.time
            dt = (now - cont_date).days + 7
            brk_list = create_break_list(self.__data_cache, days_before=dt, days_after=1, remove_past_breaks=False)

            # Creates closures as work breaks and joins them to the breaks list
            closure_list = create_closure_list(self.__data_cache, days_before=dt)
            for closure in closure_list:
                start = datetime(year=closure.year, month=closure.month, day=closure.day)
                end = start + timedelta(days=1)
                closure = WorkBreak(start, end)

                i = 0
                while i < len(brk_list):
                    joined_brk = closure.join(brk_list[i])

                    if joined_brk is not None:
                        closure = joined_brk
                        brk_list.pop(i)
                    else:
                        i += 1

                brk_list.append(closure)

            seconds = (now - cont_date).seconds  # The seconds between now and the continuous date

            # Removes seconds of breaks that occurred between now and the continuous date
            for brk in brk_list:
                seconds = max(0, seconds - brk.seconds(cont_date, now))

            self.__is_bucket_running = True
            self.__current_bucket_name = bucket['name']
            self.__clock.start_timer(seconds=bucket['time_running'] + seconds)

            self.__gui.notify()

    def __update_bucket_saved_data(self):
        bucket = self.__data_cache['bucket']
        now = self.__clock.time

        if bucket is not None:
            bucket['continuous_date'] = str(now)
            bucket['time_running'] = self.__clock.timer
        else:
            self.__data_cache['bucket'] = {
                'name': self.__current_bucket_name,
                'start_date': str(now),
                'continuous_date': str(now),
                'time_running': 0
            }

        write_data_file(self.__data_cache)
