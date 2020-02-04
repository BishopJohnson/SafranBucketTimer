# Custom packages
from src.define import Views
from src.widgets.appwidget import AppWidget
from src.widgets.keypad import Keypad
from src.widgets.partials.breaksselectelement import BreaksSelectElement

from functools import partial
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout


Builder.load_file('src/kv/breaksaddwidget.kv')


def _process_brk_data(form):
    if not isinstance(form, BreaksSelectElement):
        raise TypeError

    day = form.day
    minute = form.minute

    # Assigns hour between [0,...,23] based on the period of the day
    if form.period == 'AM':
        hour = form.hour % 12
    else:
        hour = (form.hour % 12) + 12

    return {'weekday': day.value, 'hour': hour, 'minute': minute}


class BreaksAddWidget(FloatLayout, AppWidget):
    def __init__(self, app):
        super(BreaksAddWidget, self).__init__()

        self.__app = app
        self.__keypad = None
        self.__keypad_num = 0
        self.__keypad_showing = False
        self.__start_time_widget = BreaksSelectElement(self.__app)
        self.__end_time_widget = BreaksSelectElement(self.__app)

        self.add_widget(self.__start_time_widget)
        self.add_widget(self.__end_time_widget)

        self.__start_time_widget.size_hint = (0.6, 0.2)
        self.__end_time_widget.size_hint = (0.6, 0.2)
        self.__start_time_widget.pos_hint = {'x': 0.2, 'y': 0.7}
        self.__end_time_widget.pos_hint = {'x': 0.2, 'y': 0.4}

        self.back_btn.bind(on_release=partial(self.__app.gui.open_view, Views.BREAKS_MENU))
        self.submit_btn.bind(on_release=self.submit)

    def notify(self):
        super(BreaksAddWidget, self).notify()

        self.__start_time_widget.notify()
        self.__end_time_widget.notify()

        pass

    def submit(self, *args, **kwargs):
        start = _process_brk_data(self.__start_time_widget)
        end = _process_brk_data(self.__end_time_widget)

        brk = {
            'start_weekday': start['weekday'],
            'start_hour': start['hour'],
            'start_minute': start['minute'],
            'end_weekday': end['weekday'],
            'end_hour': end['hour'],
            'end_minute': end['minute']
        }

        if self.__app.add_break(brk):
            self.__app.gui.open_view(Views.BREAKS_VIEW)
        else:
            # TODO: Open a popup stating that the break was not added.

            print('Unable to add break due to missing break attribute.')

    def _hide_keypad(self, *args, **kwargs):
        if self.__keypad_showing:
            self.__keypad_open = False
            self.__keypad.parent.remove_widget(self.__keypad)
            self.__keypad = None

    def _show_keypad(self, btn, *args, **kwargs):
        if not self.__keypad_showing:
            self.__keypad_showing = True
            self.__keypad_num = int(btn.text)
            self.__keypad = Keypad(btn,
                                   num_callback=None,
                                   enter_callback=None,
                                   cancel_callback=self._hide_keypad)

            btn.add_widget(self.__keypad)
