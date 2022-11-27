from datetime import timedelta

from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty, ObjectProperty


class DailyBlock(GridLayout):

    range_hour_text = StringProperty("")
    activities = ObjectProperty(None)

    def __init__(self, range_hour: list[timedelta], **kwargs) -> None:
        super(DailyBlock, self).__init__(**kwargs)
        self.range_hour = range_hour
        self.update_range_text()

    @property
    def range_hour(self) -> list[timedelta]:
        return self._range_hour

    @range_hour.setter
    def range_hour(self, value: list[timedelta]) -> None:
        self._range_hour = value
        self.update_range_text()

    def update_range_text(self) -> None:
        min_hour = int(self.range_hour[0].total_seconds() // 3600)
        max_hour = int(self.range_hour[1].total_seconds() // 3600)
        self.range_hour_text = f"{min_hour}:00-{max_hour}:00"

    def clean(self) -> None:
        self.activities.text = ""
