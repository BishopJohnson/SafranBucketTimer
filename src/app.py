# Custom packages
import src.fileprocessing as fp
from src.timer import Timer
from src.clock import Clock as Clk
from src.define import *
from src.widgets.popups import *
from src.widgets.rootwidget import RootWidget
from src.workbreak import WorkBreak

import csv
from datetime import date, datetime, timedelta
from functools import partial
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


def _check_bucket_name(name):
    try:
        with open(NAMES_FILE, newline='') as data_file:
            reader = csv.reader(data_file, delimiter=',')

            # Iterates for each row in the data file
            for row in reader:
                # Checks if the bucket name exists in the data file
                if row[0] == name:
                    return True
    except FileNotFoundError:
        return True  # Return true if the file cannot be found

    return False  # Return false if the bucket name was not found


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
        self.__bucket_one = None
        self.__bucket_two = None
        self.__clock = Clk()
        self.__clock_event = None
        self.__closure_list = list()
        self.__config_cache = None
        self.__data_cache = None
        self.__gui = None
        self.__log_cache = None
        self.__max_name_length = 6

    @property
    def bucket_one(self):
        return self.__bucket_one

    @property
    def bucket_two(self):
        return self.__bucket_two

    @property
    def clock(self):
        return self.__clock

    @property
    def config_cache(self):
        return self.__config_cache.copy()

    @property
    def data_cache(self):
        return self.__data_cache.copy()

    @property
    def gui(self):
        return self.__gui

    @property
    def log_cache(self):
        return self.__log_cache.copy()

    @property
    def max_name_length(self):
        return self.__max_name_length

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

        if self.is_bucket_running():
            self.__update_bucket_saved_data()

        self.__data_cache['breaks'].append(brk)
        fp.write_data_file(self.__data_cache)

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

        if self.is_bucket_running():
            self.__update_bucket_saved_data()

        self.__data_cache['closures'].append(closure)
        fp.write_data_file(self.__data_cache)

        # Recreates the closure list with the new closure
        self.__closure_list = create_closure_list(self.__data_cache)
        self.__assign_closure()

        self.__gui.notify()

        return True

    def build(self):
        super(MyApp, self).build()

        self.__config_cache = fp.import_config_file()
        self.__data_cache = fp.import_data_file()
        self.__log_cache = fp.import_log_file()

        self.__gui = RootWidget(self)
        self.__gui.open_view(Views.MAIN)

        return self.__gui

    def cancel_bucket(self, *args, **kwargs):
        bucket_one = self.__bucket_one
        bucket_two = self.__bucket_two

        if bucket_one is not None and bucket_two is not None:  # Both buckets are running
            popup = CancelBucket(self,
                                 self.__max_name_length,
                                 bucket_one_callback=partial(self.__cancel_bucket, bucket_one),
                                 bucket_two_callback=partial(self.__cancel_bucket, bucket_two))
            popup.open()
        elif bucket_one is not None:  # Only bucket one is running
            self.__cancel_bucket(bucket_one)
        elif bucket_two is not None:  # Only bucket two is running
            self.__cancel_bucket(bucket_two)

    def enter_bucket_name(self, name, *args, **kwargs):
        # Checks if the bucket name exists in the names file
        if not _check_bucket_name(name):
            popup = NameWarning(accept_callback=partial(self.start_bucket, name))
            popup.open()
        else:
            self.start_bucket(name)

    def finish_bucket(self, *args, **kwargs):
        bucket_one = self.__bucket_one
        bucket_two = self.__bucket_two

        if bucket_one is not None and bucket_two is not None:  # Both buckets are running
            popup = FinishBucket(self,
                                 self.__max_name_length,
                                 bucket_one_callback=partial(self.__finish_bucket, bucket_one),
                                 bucket_two_callback=partial(self.__finish_bucket, bucket_two))
            popup.open()
        elif bucket_one is not None:  # Only bucket one is running
            self.__finish_bucket(bucket_one)
        elif bucket_two is not None:  # Only bucket two is running
            self.__finish_bucket(bucket_two)

    def is_bucket_running(self):
        if self.__bucket_one is not None or self.__bucket_two is not None:
            return True

        return False

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
            fp.write_data_file(self.__data_cache)

            if self.is_bucket_running():
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
            fp.write_data_file(self.__data_cache)

            if self.is_bucket_running():
                self.__update_bucket_saved_data()

            # Recreates the closure list without the removed closure
            self.__closure_list = create_closure_list(self.__data_cache)
            self.__assign_closure()

            self.__gui.notify()

            return True

        return False

    def start_bucket(self, name, *args, **kwargs):
        # Checks which bucket to start
        if self.__bucket_one is None:
            self.__bucket_one = Timer(name)
            timer = self.__bucket_one
        elif self.__bucket_two is None:
            self.__bucket_two = Timer(name)
            timer = self.__bucket_two
        else:
            timer = None

        # Checks if a timer was started
        if timer is not None:
            self.__clock.add_timer(timer)
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

        fp.write_config_file(self.__config_cache)

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

    def __cancel_bucket(self, bucket):
        bucket = self.__pop_bucket(bucket)

        if bucket is not None:
            self.__clock.stop_timer(bucket)

            # Updates bucket statistics
            self.__update_bucket_saved_data()

            self.__gui.notify()

    def __finish_bucket(self, bucket):
        bucket = self.__pop_bucket(bucket)

        if bucket is not None:
            self.__clock.stop_timer(bucket)

            # Logs and updates bucket statistics
            self.__log_times(bucket)
            self.__update_bucket_saved_data()

            self.__gui.notify()

    def __log_times(self, bucket):
        if not isinstance(bucket, Timer):
            raise TypeError

        name = bucket.name
        time = bucket.seconds
        start_date = bucket.start_time
        end_date = bucket.end_time

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

        fp.write_log_file(self.__log_cache)

        self.__gui.notify()

    def __pop_bucket(self, bucket):
        if not isinstance(bucket, Timer):
            raise TypeError

        if bucket == self.__bucket_one:  # Pop bucket one
            bucket = self.__bucket_one
            self.__bucket_one = self.__bucket_two  # Move bucket two forward
            self.__bucket_two = None               #
        elif bucket == self.__bucket_two:  # Pop bucket two
            bucket = self.__bucket_two
            self.__bucket_two = None
        else:
            return None

        return bucket

    def __resume_bucket(self):
        # Handles the old bucket key
        bucket = self.__data_cache.pop('bucket', None)
        timer = self.__resume_bucket_timer(bucket)
        if bucket is not None and timer is not None:
            if self.__data_cache['bucket_one'] is None:
                self.__data_cache['bucket_one'] = bucket
            elif self.__data_cache['bucket_two'] is None:
                self.__data_cache['bucket_two'] = bucket
            else:
                self.__log_times(timer)

        bucket_one = self.__resume_bucket_timer(self.__data_cache['bucket_one'])
        bucket_two = self.__resume_bucket_timer(self.__data_cache['bucket_two'])

        # Front-loads bucket two if bucket one is empty
        if bucket_one is None and isinstance(bucket_two, Timer):
            bucket_one = bucket_two
            bucket_two = None
            self.__data_cache['bucket_one'] = self.__data_cache['bucket_two']
            self.__data_cache['bucket_two'] = None

        if isinstance(bucket_one, Timer):
            self.__bucket_one = bucket_one
            self.__clock.add_timer(self.__bucket_one)

        if isinstance(bucket_two, Timer):
            self.__bucket_two = bucket_two
            self.__clock.add_timer(self.__bucket_two)

        self.__update_bucket_saved_data()

        self.__gui.notify()

    def __resume_bucket_timer(self, bucket):
        try:
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

            return Timer(bucket['name'],
                         seconds=seconds + int(bucket['time_running']),
                         start_time=datetime.strptime(bucket['start_date'], DATE_FORMAT))
        except (TypeError, KeyError):
            return None  # Returns no timer if an error occurs

    def __update_bucket_saved_data(self):
        bucket_one = self.__data_cache['bucket_one']
        bucket_two = self.__data_cache['bucket_two']

        now = self.__clock.time

        if bucket_one is not None and isinstance(self.__bucket_one, Timer):
            bucket_one['continuous_date'] = str(now)
            bucket_one['time_running'] = self.__bucket_one.seconds
        elif isinstance(self.__bucket_one, Timer):
            self.__data_cache['bucket_one'] = {
                'name': self.__bucket_one.name,
                'start_date': str(self.__bucket_one.start_time),
                'continuous_date': str(now),
                'time_running': self.__bucket_one.seconds
            }
        else:
            self.__data_cache['bucket_one'] = None

        if bucket_two is not None and isinstance(self.__bucket_two, Timer):
            bucket_two['continuous_date'] = str(now)
            bucket_two['time_running'] = self.__bucket_two.seconds
        elif isinstance(self.__bucket_two, Timer):
            self.__data_cache['bucket_two'] = {
                'name': self.__bucket_two.name,
                'start_date': str(self.__bucket_two.start_time),
                'continuous_date': str(now),
                'time_running': self.__bucket_two.seconds
            }
        else:
            self.__data_cache['bucket_two'] = None

        fp.write_data_file(self.__data_cache)
