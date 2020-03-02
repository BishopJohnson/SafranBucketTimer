# Custom packages
from src.widgets.popups.dualbuttonpopup import DualButtonPopup


class TriButtonPopup(DualButtonPopup):
    def __init__(self, mid_btn_callback=None, **kwargs):
        super(TriButtonPopup, self).__init__(**kwargs)

        self._mid_btn_callback = mid_btn_callback

    def mid_btn(self):
        if callable(self._mid_btn_callback):
            self._mid_btn_callback()

        self.dismiss()
