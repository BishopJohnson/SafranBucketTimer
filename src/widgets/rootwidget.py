# Custom packages
from src.widgets.appwidget import AppWidget
from src.widgets.mainwidget import MainWidget
from src.widgets.optionswidget import OptionsWidget

from kivy.uix.floatlayout import FloatLayout


class RootWidget(FloatLayout, AppWidget):
    def __init__(self, app):
        super(RootWidget, self).__init__()

        self.__app = app
        self.__widget = None

    def show_main(self):
        self.clear_widgets()

        self.__widget = MainWidget(self.__app)
        self.__widget.notify()

        self.add_widget(self.__widget)

    def show_options(self):
        self.clear_widgets()

        self.__widget = OptionsWidget(self.__app)
        self.__widget.notify()

        self.add_widget(self.__widget)

    def notify(self):
        super(RootWidget, self).notify()

        if self.__widget is not None:
            self.__widget.notify()

    def update(self):
        super(RootWidget, self).update()

        if self.__widget is not None:
            self.__widget.update()
