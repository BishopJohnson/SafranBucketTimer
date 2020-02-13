from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput


Builder.load_file('src/kv/partials/tablelayout.kv')


class TableLayout1(BoxLayout):
    def __init__(self, **kwargs):
        super(TableLayout1, self).__init__(**kwargs)


class TableLayout2(BoxLayout):
    def __init__(self, **kwargs):
        super(TableLayout2, self).__init__(**kwargs)


class TableText(Label):
    def __init__(self, **kwargs):
        super(TableText, self).__init__(**kwargs)


class TableTextInput(TextInput):
    def __init__(self, **kwargs):
        super(TableTextInput, self).__init__(**kwargs)
