from define import DATA_FILE
from define import LOG_FILE

import csv
import json
from pathlib import Path


def create_data_file():
    # Checks if the file does not exist
    if not Path(DATA_FILE).exists():
        file = open(DATA_FILE, 'w', newline='')

        json.dump([{"name": None, "time": None}], file)


def create_log_file():
    # Checks if the file does not exist
    if not Path(LOG_FILE).exists():
        with open(LOG_FILE, 'w', newline='') as log:
            writer = csv.writer(log, delimiter=',')

            # Create the header
            writer.writerow(['bucket_number', 'work_time_hrs', 'work_time_sec', 'start_date', 'end_date'])