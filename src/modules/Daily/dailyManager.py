from modules.Daily.dailyBlock import DailyBlock
from modules.Utilities.radioButton import RadioButton

from kivy.properties import ObjectProperty, StringProperty
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from datetime import date, timedelta


kv = Builder.load_file("kvFiles/Daily.kv")


def get_divisors(n: int):
    yield 1
    for i in range(2, n//2):
        if (n % i == 0):
            yield i
    yield n


class DailyManager(Screen):

    grid = ObjectProperty(None)
    date_label = StringProperty(None)
    separation_options = ObjectProperty(None)

    def __init__(self, min_hour: int = 6, max_hour: int = 24, base_separation: int = 1, **kwargs) -> None:
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
            self.create_blocks()
            self.load_separation_options()

    def go_back(self) -> None:
        self.manager.transition.direction = "right"
        self.manager.current = "Main"

    def create_blocks(self) -> None:
        for i in range(self.num_blocks):
            begin = self.min_hour+i*self.base_separation
            end = begin+self.base_separation
            block = DailyBlock([begin, end])
            self.grid.add_widget(block, index=1)
            self.blocks.append(block)

    def add_blocks(self, num_blocks) -> None:
        if num_blocks > 0:
            for _ in range(num_blocks):
                block = DailyBlock([timedelta(), timedelta()])
                self.grid.add_widget(block, index=1)
                self.blocks.append(block)
            return

        for i in range(abs(num_blocks)):
            self.grid.remove_widget(self.blocks[-1])
            self.blocks.pop()

    def clear_blocks(self) -> None:
        for block in self.blocks:
            block.clean()

    def change_day(self, next: bool) -> None:
        self.current_date = self.current_date + timedelta(days=int(next)*2-1)
        self.date_label = str(self.current_date)
        self.clear_blocks()

    def update_separation(self, value: int) -> None:

        old_num = self.num_blocks
        self.base_separation = timedelta(hours=value)
        self.num_blocks = int(
            (self.max_hour - self.min_hour) / self.base_separation)

        self.add_blocks(self.num_blocks-old_num)

        for i, block in enumerate(self.blocks):
            begin = self.min_hour+i*self.base_separation
            end = begin+self.base_separation

            block.range_hour = [begin, end]

    def load_separation_options(self) -> None:

        total_range_hour = int(
            (self.max_hour - self.min_hour).total_seconds() // 3600)
        divisors = get_divisors(total_range_hour)

        for div in divisors:

            radioButton = RadioButton(str(div), "separation_options", div, on_selected=self.update_separation)
            self.separation_options.add_widget(radioButton)

            if (div == 1):
                radioButton.checkbox.active = True
