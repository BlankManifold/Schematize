from typing import Callable
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.properties import ObjectProperty

kv = Builder.load_file("kvFiles/RadioButton.kv")


class RadioButton(GridLayout):

    checkbox = ObjectProperty(None)

    def __init__(self, label_text: str, group: str, data: object, *, on_selected: Callable, **kwargs):
        self.label_text = label_text
        self.group = group
        self.data = data
        self.on_selected = on_selected

        super(RadioButton, self).__init__(**kwargs)
    