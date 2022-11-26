from datetime import date, timedelta

from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty


from modules.Daily.dailyBlock import DailyBlock
kv = Builder.load_file("kvFiles/Daily.kv")


class DailyManager(Screen):

    grid = ObjectProperty(None)
    date_label = StringProperty(None)

    def __init__(self, min_hour: int = 6, max_hour: int = 22, base_separation: int = 4, **kwargs) -> None:
        super(DailyManager, self).__init__(**kwargs)

        self.current_date = date.today()
        self.date_label = str(self.current_date)
        self.min_hour = timedelta(hours=min_hour)
        self.max_hour = timedelta(hours=max_hour)
        self.base_separation = timedelta(hours=base_separation)
        self.num_blocks = int(
            (self.max_hour - self.min_hour) / self.base_separation)
        self.loaded = False
        self.blocks = list[DailyBlock]()

    def on_pre_enter(self) -> None:
        if not self.loaded:
            self.loaded = True
            self.add_blocks()

    def go_back(self) -> None:
        self.manager.current = "Main"

    def add_blocks(self) -> None:
        for i in range(self.num_blocks):
            begin = self.min_hour+i*self.base_separation
            end = begin+self.base_separation
            block = DailyBlock([begin, end])
            self.grid.add_widget(block, index=1)
            self.blocks.append(block)

    def clear_blocks(self) -> None:
        for block in self.blocks:
            block.clean()

    def change_day(self, next: bool) -> None:
        self.current_date = self.current_date + timedelta(days=int(next)*2-1)
        self.date_label = str(self.current_date)
        self.clear_blocks()
