from __future__ import annotations

from datetime import timedelta

from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty, ObjectProperty


class DailyBlock(GridLayout):

    activities = StringProperty("")
    text_input = ObjectProperty(None)
    range_hour_text = StringProperty("")
    add_button = ObjectProperty(None)
    remove_button = ObjectProperty(None)


    def __init__(self, pos_id:int, range_hour: list[timedelta], activities: str = "", **kwargs) -> None:
        self.pos_id = pos_id
        self.activities = activities
        self.range_hour_text = ""
        self.range_hour = range_hour
        super(DailyBlock, self).__init__(**kwargs)

    def __repr__(self) -> str:
        return f"{self.range_hour_text} {self.activities}"

    @property
    def range_hour(self) -> list[timedelta]:
        return self._range_hour
    
    @property
    def pos_id(self) -> int:
        return self._pos_id
        
    @property
    def range_hour_int(self) -> int:
        return int((self.range_hour[1]-self.range_hour[0]).total_seconds() // 3600)

    @range_hour.setter
    def range_hour(self, value: list[timedelta]) -> None:
        self._range_hour = value
        self.update_range_text()
    
    @pos_id.setter
    def pos_id(self, value: int) -> None:
        self._pos_id = value
        self.activities = str(self.pos_id)
    
    def compose_with(self, other: DailyBlock) -> None:
        added_activities = f"{self.activities}\n{other.activities}"
        self.activities = added_activities
        self.range_hour = [self.range_hour[0], other.range_hour[1]]

    def update_range_text(self) -> None:
        min_hour = int(self.range_hour[0].total_seconds() // 3600)
        max_hour = int(self.range_hour[1].total_seconds() // 3600)
        self.range_hour_text = f"{min_hour}:00-{max_hour}:00"

    def clean(self) -> None:
        self.activities = ""
    
    def save_text(self):
        self.activities = self.text_input.text
