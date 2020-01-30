from kivy.lang import Builder
from kivy.uix.popup import Popup


Builder.load_file('src/kv/popups.kv')


class NameWarning(Popup):
    def __init__(self, app):
        super(NameWarning, self).__init__()
        self.__app = app

    def accept(self):
        self.__app.start_bucket()
        self.dismiss()

    def cancel(self):
        self.__app.cancel_bucket_name()
        self.dismiss()
