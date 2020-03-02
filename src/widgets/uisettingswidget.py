# Custom packages
from src.define import CONFIG_FILE_KEYS
from src.define import Views
from src.widgets.appwidget import AppWidget
from src.widgets.partials.tablelayout import *

from functools import partial
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput


Builder.load_file('src/kv/uisettingswidget.kv')


def _format_config(config, key, value):
    if key in CONFIG_FILE_KEYS:
        # TODO: Assign the keys in a smarter fashion that doesn't rely on knowing the types in this function.
        if key == 'team_name':
            config.update(team_name=value)
        elif key == 'goal_time':
            config.update(goal_time=value)

        return config
    else:
        raise KeyError


def _config_key2name(key):
    if key in CONFIG_FILE_KEYS:
        # TODO: Assign the keys in a smarter fashion that doesn't rely on knowing the types in this function.
        if key == 'team_name':
            return 'TEAM NAME'
        elif key == 'goal_time':
            return 'GOAL TIME (Hrs)'
    else:
        raise KeyError


class UISettingsWidget(FloatLayout, AppWidget):
    def __init__(self, app):
        super(UISettingsWidget, self).__init__()

        self.__app = app
        self.__config = {}

        self.back_btn.bind(on_release=partial(self.__app.gui.open_view, Views.OPTIONS_MENU))
        self.apply_btn.bind(on_release=self.apply)

    def apply(self, *args, **kwargs):
        config = {}

        for key in self.__config:
            config = _format_config(config, key, self.__config[key].text)

        self.__app.update_config(config)

    def notify(self):
        super(UISettingsWidget, self).notify()

        self.__update_settings()

        pass

    def __update_settings(self):
        self.table.clear_widgets()
        self.__config.clear()

        i = 0
        for key in CONFIG_FILE_KEYS:
            if i % 2 == 0:
                layout = TableLayout1()
            else:
                layout = TableLayout2()

            label = TableText(text='  {}:'.format(_config_key2name(key)))
            text_input = TableTextInput(text=str(self.__app.config_cache[key]))

            layout.add_widget(label)
            layout.add_widget(text_input)

            self.table.add_widget(layout)
            self.__config = _format_config(self.__config, key, text_input)

            i += 1
