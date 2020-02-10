# Custom packages
from src.widgets.appwidget import AppWidget

from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.relativelayout import RelativeLayout


Builder.load_file('src/kv/partials/selectelement.kv')


class SelectElement(RelativeLayout, AppWidget):
    def __init__(self,
                 app,
                 *args,
                 element_callback=None,
                 increment_callback=None,
                 decrement_callback=None,
                 orientation='vertical',
                 **kwargs):
        super(SelectElement, self).__init__(**kwargs)

        self._app = app
        self.layout.orientation = orientation
        self._decrement_callback = decrement_callback
        self._element_callback = element_callback
        self._increment_callback = increment_callback
        self.__element_btn = SelectElementBtn(text='',
                                              color=(0, 0, 0, 1),
                                              background_normal='',
                                              background_color=(1, 1, 1, 1))
        self.__increment_btn = SelectElementBtn(text='+',
                                                color=(1, 1, 1, 1))
        self.__decrement_btn = SelectElementBtn(text='-',
                                                color=(1, 1, 1, 1))

        if orientation == 'horizontal':
            self.layout.add_widget(self.__decrement_btn)
            self.layout.add_widget(self.__element_btn)
            self.layout.add_widget(self.__increment_btn)
        elif orientation == 'vertical':
            self.layout.add_widget(self.__increment_btn)
            self.layout.add_widget(self.__element_btn)
            self.layout.add_widget(self.__decrement_btn)
        else:
            raise ValueError

        self.__decrement_btn.bind(on_release=self.decrement)
        self.__element_btn.bind(on_release=self.element)
        self.__increment_btn.bind(on_release=self.increment)

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

        self.__element_btn.text = text


class SelectElementBtn(Button):
    def __init__(self, *args, **kwargs):
        super(SelectElementBtn, self).__init__(**kwargs)
