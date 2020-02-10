# Custom packages
from src.define import Views
from src.widgets.appwidget import AppWidget

from functools import partial
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout


Builder.load_file('src/kv/breaksmenuwidget.kv')


class BreaksMenuWidget(FloatLayout, AppWidget):
    def __init__(self, app):
        super(BreaksMenuWidget, self).__init__()

        self.__app = app

        self.back_btn.bind(on_release=partial(self.__app.gui.open_view, Views.OPTIONS_MENU))
        self.assign_breaks_btn.bind(on_release=partial(self.__app.gui.open_view, Views.BREAKS_ADD))
        self.closures_btn.bind(on_release=partial(self.__app.gui.open_view, Views.BREAKS_CLOSURES))
        self.view_breaks_btn.bind(on_release=partial(self.__app.gui.open_view, Views.BREAKS_VIEW))
