# Custom packages
from src.widgets.popups.dualbuttonpopup import DualButtonPopup

from kivy.lang import Builder


Builder.load_file('src/kv/popups/namewarning.kv')


class NameWarning(DualButtonPopup):
    def __init__(self, accept_callback=None, cancel_callback=None, **kwargs):
        super(NameWarning, self).__init__(left_btn_callback=cancel_callback,
                                          right_btn_callback=accept_callback,
                                          **kwargs)
