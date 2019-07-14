from kivy.uix.bubble import Bubble
from math import fabs


class Keypad(Bubble):
    def __init__(self, widget):
        super(Keypad, self).__init__()
        self.widget = widget
        self.num = ''
        self.x = widget.x - fabs((self.width * 0.5) - (widget.width * 0.5))
        self.y = widget.y - self.height
