# Custom packages
from src.define import Views
from src.widgets.appwidget import AppWidget
from src.widgets.breaksaddwidget import BreaksAddWidget
from src.widgets.breaksclosurewidget import BreaksClosuresWidget
from src.widgets.breaksmenuwidget import BreaksMenuWidget
from src.widgets.breaksviewwidget import BreaksViewWidget
from src.widgets.mainwidget import MainWidget
from src.widgets.optionswidget import OptionsWidget
from src.widgets.uisettingswidget import UISettingsWidget

from kivy.uix.floatlayout import FloatLayout


class RootWidget(FloatLayout, AppWidget):
    def __init__(self, app):
        super(RootWidget, self).__init__()

        self.__app = app
        self.__widget = None

    def open_view(self, view, *args, **kwargs):
        if not isinstance(view, Views):
            raise TypeError

        if view == Views.MAIN:
            self.__set_widget(MainWidget(self.__app))
        elif view == Views.OPTIONS_MENU:
            self.__set_widget(OptionsWidget(self.__app))
        elif view == Views.BREAKS_MENU:
            self.__set_widget(BreaksMenuWidget(self.__app))
        elif view == Views.BREAKS_VIEW:
            self.__set_widget(BreaksViewWidget(self.__app))
        elif view == Views.BREAKS_ADD:
            self.__set_widget(BreaksAddWidget(self.__app))
        elif view == Views.BREAKS_CLOSURES:
            self.__set_widget(BreaksClosuresWidget(self.__app))
        elif view == Views.UI_SETTINGS:
            self.__set_widget(UISettingsWidget(self.__app))
        else:
            print('No such view {}'.format(view))

    def notify(self):
        super(RootWidget, self).notify()

        if self.__widget is not None:
            self.__widget.notify()

    def update(self):
        super(RootWidget, self).update()

        if self.__widget is not None:
            self.__widget.update()

    def __set_widget(self, widget):
        if isinstance(widget, AppWidget):
            self.clear_widgets()

            self.__widget = widget
            self.notify()
            self.update()

            self.add_widget(self.__widget)
