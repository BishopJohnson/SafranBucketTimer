# Custom packages
from src.define import Views
from src.widgets.appwidget import AppWidget

from functools import partial
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout


Builder.load_file('src/kv/optionswidget.kv')


class OptionsWidget(FloatLayout, AppWidget):
    def __init__(self, app):
        super(OptionsWidget, self).__init__()

        self.__app = app

        self.back_btn.bind(on_release=partial(self.__app.gui.open_view, Views.MAIN))
        self.breaks_btn.bind(on_release=partial(self.__app.gui.open_view, Views.BREAKS_MENU))
        self.ui_btn.bind(on_release=partial(self.__app.gui.open_view, Views.UI_SETTINGS))
