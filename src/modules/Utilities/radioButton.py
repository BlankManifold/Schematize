from typing import Callable, TypeVar
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.properties import ObjectProperty

kv = Builder.load_file("kvFiles/RadioButton.kv")


class RadioButton(GridLayout):

    checkbox = ObjectProperty(None)

    T = TypeVar('T')
    def __init__(self, label_text: str, group: str, data: T, *, on_selected: Callable[[T,bool],object], **kwargs) -> None:
        self.label_text = label_text
        self.group = group
        self.data = data
        self.on_selected = on_selected
        
        super(RadioButton, self).__init__(**kwargs)
    