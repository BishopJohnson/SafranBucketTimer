# Custom packages
from src.define import CONFIG_FILE
from src.define import CONFIG_FILE_KEYS
from src.define import DATA_FILE
from src.define import DATA_FILE_KEYS
from src.define import LOG_FILE

import csv
import json
from datetime import date
from pathlib import Path


def create_config_file():
    # Checks if the file does not exist
    if not Path(CONFIG_FILE).exists():
        file = open(CONFIG_FILE, 'w', newline='')

        config = {
            'team_name': '',
            'goal_time': '0.00'
        }

        json.dump(config, file, sort_keys=False, indent=4)


def create_data_file():
    # Checks if the file does not exist
    if not Path(DATA_FILE).exists():
        file = open(DATA_FILE, 'w', newline='')

        data = {
            'bucket': None,
            'breaks': [],
            'closures': []
        }

        json.dump(data, file, sort_keys=False, indent=4)


def create_log_file():
    # Checks if the file does not exist
    if not Path(LOG_FILE).exists():
        with open(LOG_FILE, 'w', newline='') as log:
            writer = csv.writer(log, delimiter=',')

            # Create the header
            writer.writerow(['bucket_number', 'work_time_hrs', 'work_time_sec', 'start_date', 'end_date'])


def import_config_file():
    create_config_file()  # Creates file if it does not exist

    file = open(CONFIG_FILE, 'r', newline='')

    config = _format_config(json.load(file))

    return config


def import_data_file():
    create_data_file()  # Creates file if it does not exist

    file = open(DATA_FILE, 'r', newline='')

    data = _format_data(json.load(file))

    return data


def write_config_file(config):
    config = _format_config(config)

    file = open(CONFIG_FILE, 'w', newline='')

    json.dump(config, file, sort_keys=False, indent=4)


def write_data_file(data):
    data = _format_data(data)

    # Removes closures that occurred more than one year ago
    for closure in data['closures']:
        today = date.today()
        day = date(closure['year'], closure['month'], closure['day'])

        if (today - day).days > 365:
            data['closures'].remove(closure)

    file = open(DATA_FILE, 'w', newline='')

    json.dump(data, file, sort_keys=False, indent=4)


def _format_config(config):
    for key in CONFIG_FILE_KEYS:
        # TODO: Assign the values in a smarter fashion that doesn't rely on knowing the types in this function.
        if key not in config:
            if key == 'team_name':
                config.update(team_name='')
            elif key == 'goal_time':
                config.update(goal_time='0.00')

    return config


def _format_data(data):
    for key in DATA_FILE_KEYS:
        # TODO: Assign the values in a smarter fashion that doesn't rely on knowing the types in this function.
        if key not in data:
            if key == 'bucket':
                data.update(bucket=None)
            elif key == 'breaks':
                data.update(breaks=[])
            elif key == 'closures':
                data.update(closures=[])

    return data
