from kivy.uix.popup import Popup


class DualButtonPopup(Popup):
    def __init__(self, left_btn_callback=None, right_btn_callback=None, **kwargs):
        super(DualButtonPopup, self).__init__(**kwargs)

        self._left_btn_callback = left_btn_callback
        self._right_btn_callback = right_btn_callback

    def left_btn(self):
        if callable(self._left_btn_callback):
            self._left_btn_callback()

        self.dismiss()

    def right_btn(self):
        if callable(self._right_btn_callback):
            self._right_btn_callback()

        self.dismiss()

