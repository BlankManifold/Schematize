from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty

class DailyBlock(GridLayout):
    
    hour_range = ObjectProperty(None)
    activities = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(DailyBlock, self).__init__(**kwargs)