# Custom packages
from src.widgets.appwidget import AppWidget

from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout


Builder.load_file('src/kv/partials/selectelement.kv')


class SelectElement(RelativeLayout, AppWidget):
    def __init__(self, app, *args, element_callback=None, increment_callback=None, decrement_callback=None, **kwargs):
        super(SelectElement, self).__init__()

        self._app = app
        self._decrement_callback = decrement_callback
        self._element_callback = element_callback
        self._increment_callback = increment_callback

        self.decrement_btn.bind(on_release=self.decrement)
        self.element_btn.bind(on_release=self.element)
        self.increment_btn.bind(on_release=self.increment)

    def decrement(self, *args, **kwargs):
        if callable(self._decrement_callback):
            self._decrement_callback()

        pass

    def element(self, *args, **kwargs):
        if callable(self._element_callback):
            self._element_callback()

        pass

    def increment(self, *args, **kwargs):
        if callable(self._increment_callback):
            self._increment_callback()

        pass

    def set_text(self, text):
        if type(text) is not str:
            raise TypeError

        self.element_btn.text = text
