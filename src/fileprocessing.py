# Custom packages
from src.define import CONFIG_FILE
from src.define import CONFIG_FILE_KEYS
from src.define import DATA_FILE
from src.define import DATA_FILE_KEYS
from src.define import LOG_FILE
from src.define import LOG_FILE_HEADER

import csv
import json
from datetime import date
from pathlib import Path


def create_config_file():
    # Checks if the file does not exist
    if not Path(CONFIG_FILE).exists():
        with open(CONFIG_FILE, 'w', newline='') as file:
            config = {
                'team_name': '',
                'goal_time': '0.00'
            }

            json.dump(config, file, sort_keys=False, indent=4)

            file.close()


def create_data_file():
    # Checks if the file does not exist
    if not Path(DATA_FILE).exists():
        with open(DATA_FILE, 'w', newline='') as file:
            data = {
                'bucket_one': None,
                'bucket_two': None,
                'breaks': [],
                'closures': []
            }

            json.dump(data, file, sort_keys=False, indent=4)

            file.close()


def create_log_file():
    # Checks if the file does not exist
    if not Path(LOG_FILE).exists():
        with open(LOG_FILE, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',')

            # Create the header
            writer.writerow(LOG_FILE_HEADER)

            file.close()


def import_config_file():
    create_config_file()  # Creates file if it does not exist

    with open(CONFIG_FILE, 'r', newline='') as file:
        config = _format_config(json.load(file))

        file.close()

    return config


def import_data_file():
    create_data_file()  # Creates file if it does not exist

    with open(DATA_FILE, 'r', newline='') as file:
        data = _format_data(json.load(file))

        file.close()

    return data


def import_log_file():
    create_log_file()  # Creates file if it does not exist

    log = list()

    with open(LOG_FILE, 'r', newline='') as file:
        reader = csv.reader(file, delimiter=',')

        next(reader)  # Skip the headers

        for row in reader:
            log.append(row)

        file.close()

    return log


def write_config_file(config):
    config = _format_config(config)

    with open(CONFIG_FILE, 'w', newline='') as file:
        json.dump(config, file, sort_keys=False, indent=4)

        file.close()


def write_data_file(data):
    data = _format_data(data)

    # Removes closures that occurred more than one year ago
    for closure in data['closures']:
        today = date.today()
        day = date(closure['year'], closure['month'], closure['day'])

        if (today - day).days > 365:
            data['closures'].remove(closure)

    with open(DATA_FILE, 'w', newline='') as file:
        json.dump(data, file, sort_keys=False, indent=4)

        file.close()


def write_log_file(log):
    with open(LOG_FILE, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')

        writer.writerow(LOG_FILE_HEADER)

        for row in log:
            writer.writerow(row)

        file.close()


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
            if key == 'bucket_one':
                data.update(bucket_one=None)
            if key == 'bucket_two':
                data.update(bucket_two=None)
            elif key == 'breaks':
                data.update(breaks=[])
            elif key == 'closures':
                data.update(closures=[])

    return data
