from functools import partial
from kivy.lang import Builder
from kivy.uix.bubble import Bubble
from math import fabs


Builder.load_file('src/kv/keypad.kv')


class Keypad(Bubble):
    def __init__(self, widget, max_length=8, num_callback=None, enter_callback=None, cancel_callback=None, **kwargs):
        super(Keypad, self).__init__(**kwargs)

        self.__widget = widget
        self.__num = ''
        self.__max_length = max_length
        self.__num_callback = num_callback

        self.x = widget.x - fabs((self.width * 0.5) - (widget.width * 0.5))
        self.y = widget.y - self.height

        self.btn_0.bind(on_release=partial(self.__num_press, self.btn_0.text))
        self.btn_1.bind(on_release=partial(self.__num_press, self.btn_1.text))
        self.btn_2.bind(on_release=partial(self.__num_press, self.btn_2.text))
        self.btn_3.bind(on_release=partial(self.__num_press, self.btn_3.text))
        self.btn_4.bind(on_release=partial(self.__num_press, self.btn_4.text))
        self.btn_5.bind(on_release=partial(self.__num_press, self.btn_5.text))
        self.btn_6.bind(on_release=partial(self.__num_press, self.btn_6.text))
        self.btn_7.bind(on_release=partial(self.__num_press, self.btn_7.text))
        self.btn_8.bind(on_release=partial(self.__num_press, self.btn_8.text))
        self.btn_9.bind(on_release=partial(self.__num_press, self.btn_9.text))

        if callable(enter_callback):
            self.btn_enter.bind(on_release=partial(enter_callback, self.__num))

        if callable(cancel_callback):
            self.btn_cancel.bind(on_release=cancel_callback)

    @property
    def num(self):
        return self.__num

    def __num_press(self, num, *args, **kwargs):
        self.__num += str(num)

        # Checks if num is longer than the specified length
        if len(self.__num) > self.__max_length:
            text = '{}...'.format(self.__num[:self.__max_length])
        else:
            text = self.__num

        self.num_text.text = text

        if callable(self.__num_callback):
            self.__num_callback()
