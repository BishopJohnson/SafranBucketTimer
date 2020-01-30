from math import floor

SEC_PER_HOUR = 3600
SEC_PER_MIN = 60
MIN_PER_HOUR = 60
DATA_FILE = 'dat.json'
LOG_FILE = 'bucket_log.csv'
NAMES_FILE = 'Alpha Numberic Bucket Numbers.csv'

MAIN_VIEW = 'main'
OPTIONS_VIEW = 'options'


def hours_minutes_seconds(seconds):
    hours = floor(seconds / SEC_PER_HOUR)
    seconds = seconds % SEC_PER_HOUR

    minutes = floor(seconds / SEC_PER_MIN)
    seconds = seconds % SEC_PER_MIN

    return hours, minutes, seconds
