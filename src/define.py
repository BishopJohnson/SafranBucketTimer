from enum import Enum
from math import floor


DATA_File_KEYS = [
    'bucket',
    'breaks',
    'closures'
]
BREAK_KEYS = [
    'start_weekday',
    'start_hour',
    'start_minute',
    'end_weekday',
    'end_hour',
    'end_minute'
]
CLOSURE_KEYS = [
    'year',
    'month',
    'day'
]
DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
SEC_PER_HOUR = 3600
SEC_PER_MIN = 60
MIN_PER_HOUR = 60
DATA_FILE = 'dat.json'
LOG_FILE = 'bucket_log.csv'
NAMES_FILE = 'Alpha Numberic Bucket Numbers.csv'


def hours_minutes_seconds(seconds):
    hours = floor(seconds / SEC_PER_HOUR)
    seconds = seconds % SEC_PER_HOUR

    minutes = floor(seconds / SEC_PER_MIN)
    seconds = seconds % SEC_PER_MIN

    return hours, minutes, seconds


class Days(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class Views(Enum):
    MAIN = 1
    OPTIONS_MENU = 2
    BREAKS_MENU = 3
    BREAKS_VIEW = 4
    BREAKS_ADD = 5
    BREAKS_CLOSURES = 6
