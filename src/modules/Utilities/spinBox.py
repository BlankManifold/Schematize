from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.gridlayout import GridLayout

kv = Builder.load_file("kvFiles/SpinBox.kv")


class SpinBox(GridLayout):

    current_value = NumericProperty(0)
    label_text = StringProperty("")

    def __init__(self, label_text:str, min_value: int = 0, max_value: int = 24, step: int = 1, initial_value: int = 0,  **kwargs) -> None:
        
        self.label_text = label_text
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.current_value = initial_value

        super(SpinBox, self).__init__(**kwargs)

    def on_up(self) -> None:
        self.current_value = min(self.current_value+self.step, self.max_value)

    def on_down(self) -> None:
        self.current_value = max(self.current_value-self.step, self.min_value)

    def on_input_value(self, value: str) -> None:
        try:
            value_num = int(float(value))
        except:
            return
        value_num = min(value_num, self.max_value)
        value_num = max(value_num, self.min_value)

        self.current_value = value_num
