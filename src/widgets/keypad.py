from functools import partial
from kivy.lang import Builder
from kivy.uix.bubble import Bubble
from math import fabs


Builder.load_file('src/kv/keypad.kv')


class Keypad(Bubble):
    def __init__(self, widget, *args, num_callback=None, enter_callback=None, cancel_callback=None, **kwargs):
        super(Keypad, self).__init__()
        self.widget = widget
        self.num = ''
        self.x = widget.x - fabs((self.width * 0.5) - (widget.width * 0.5))
        self.y = widget.y - self.height

        if num_callback is not None and callable(num_callback):
            self.btn_0.bind(on_release=partial(num_callback, self.btn_0.text))
            self.btn_1.bind(on_release=partial(num_callback, self.btn_1.text))
            self.btn_2.bind(on_release=partial(num_callback, self.btn_2.text))
            self.btn_3.bind(on_release=partial(num_callback, self.btn_3.text))
            self.btn_4.bind(on_release=partial(num_callback, self.btn_4.text))
            self.btn_5.bind(on_release=partial(num_callback, self.btn_5.text))
            self.btn_6.bind(on_release=partial(num_callback, self.btn_6.text))
            self.btn_7.bind(on_release=partial(num_callback, self.btn_7.text))
            self.btn_8.bind(on_release=partial(num_callback, self.btn_8.text))
            self.btn_9.bind(on_release=partial(num_callback, self.btn_9.text))

        if enter_callback is not None and callable(enter_callback):
            self.btn_enter.bind(on_release=enter_callback)

        if cancel_callback is not None and callable(cancel_callback):
            self.btn_cancel.bind(on_release=cancel_callback)
