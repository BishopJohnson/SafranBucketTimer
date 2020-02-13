# Custom packages
from src.define import Days
from src.define import Views
from src.widgets.appwidget import AppWidget
from src.widgets.partials.tablelayout import *

from functools import partial
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from operator import itemgetter


Builder.load_file('src/kv/breaksviewwidget.kv')


def format_time(weekday, hour, minute):
    if weekday == Days.MONDAY.value:
        weekday_text = 'Mon.'
    elif weekday == Days.TUESDAY.value:
        weekday_text = 'Tue.'
    elif weekday == Days.WEDNESDAY.value:
        weekday_text = 'Wed.'
    elif weekday == Days.THURSDAY.value:
        weekday_text = 'Thu.'
    elif weekday == Days.FRIDAY.value:
        weekday_text = 'Fri.'
    elif weekday == Days.SATURDAY.value:
        weekday_text = 'Sat.'
    elif weekday == Days.SUNDAY.value:
        weekday_text = 'Sun.'
    else:
        weekday_text = ''

    period = 'AM'  # Assume AM

    # Checks the period of the day
    if hour == 0:
        hour = 12
    elif hour >= 12:
        period = 'PM'

        # Checks if hour needs to recycle
        if hour > 12:
            hour = hour % 12

    return f'{weekday_text} {hour}:{minute:02d} {period}'


class BreaksViewWidget(FloatLayout, AppWidget):
    def __init__(self, app):
        super(BreaksViewWidget, self).__init__()

        self.__app = app

        self.back_btn.bind(on_release=partial(self.__app.gui.open_view, Views.BREAKS_MENU))
        self.table.bind(minimum_height=self.table.setter('height'))

        self.update_table()

    def notify(self):
        super(BreaksViewWidget, self).notify()

        self.update_table()

    def update_table(self):
        self.table.clear_widgets()  # Clears the table

        brk_list = self.__app.data_cache['breaks']

        # Sorts to have breaks that occur sooner at the front
        if len(brk_list) > 1:
            brk_list = sorted(brk_list, key=itemgetter('start_weekday', 'start_hour', 'start_minute'))

        length = max(len(brk_list), 10)

        for i in range(0, length):
            # Alternate style every row
            if i % 2 == 0:
                layout = TableLayout1()
            else:
                layout = TableLayout2()

            if i < len(brk_list):
                brk = brk_list[i]
                start = format_time(brk['start_weekday'], brk['start_hour'], brk['start_minute'])
                end = format_time(brk['end_weekday'], brk['end_hour'], brk['end_minute'])

                # The delete button
                btn = Button(text='DEL')
                btn.size_hint_x = 0.2
                btn.bind(on_release=partial(self.__app.remove_break, brk))

                layout.add_widget(btn)
                layout.add_widget(TableText(text='  {} - {}'.format(start, end)))

            self.table.add_widget(layout)
