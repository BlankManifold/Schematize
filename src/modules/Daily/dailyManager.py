from datetime import date, timedelta
from typing import Iterator, Optional

from modules.Daily.dailyBlock import DailyBlock
from modules.Utilities.radioButton import RadioButton

from kivy.properties import ObjectProperty, StringProperty
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen


kv = Builder.load_file("kvFiles/Daily.kv")


def get_divisors(n: int) -> Iterator[int]:
    yield 1
    for i in range(2, n//2+1):
        if (n % i == 0):
            yield i
    yield n


class DailyManager(Screen):

    grid = ObjectProperty(None)
    date_label = StringProperty(None)
    separation_options = ObjectProperty(None)

    def __init__(self, min_hour: int = 6, max_hour: int = 22, base_separation: int = 1, separations_list: Optional[list[int]] = None, **kwargs) -> None:
        super(DailyManager, self).__init__(**kwargs)

        if separations_list is not None:
            pass

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

            block = DailyBlock(i, [begin, end])
            self.grid.add_widget(block, index=1)
            self.blocks.append(block)

            block.add_button.bind(on_release=lambda instance: self.add_block(
                instance.parent.parent.pos_id))
            block.remove_button.bind(
                on_release=lambda instance: self.remove_block(instance.parent.parent.pos_id))

    def reduce_blocks(self, from_n: int, to_n: int) -> None:
        div, rem = divmod(from_n, to_n)

        to_be_removed = []

        for i in range(rem):
            self.blocks[-rem-1].compose_with(self.blocks[-rem+i])
            to_be_removed.append(self.blocks[-rem+i])

        for i in range(0, from_n-rem, div):
            for sum_id in range(i+1, i+div):
                self.blocks[i].compose_with(self.blocks[sum_id])
                to_be_removed.append(self.blocks[sum_id])

        for block in to_be_removed:
            self.grid.remove_widget(block)
            self.blocks.remove(block)

        if rem:
            for i, block in enumerate(self.blocks):
                begin = self.min_hour + i*self.base_separation
                end = begin + self.base_separation
                block.range_hour = [begin, end]

        for i, block in enumerate(self.blocks):
            block.pos_id = i

    def add_blocks(self, from_n: int, to_n: int) -> None:
        for i in range(to_n - from_n):
            block = DailyBlock(from_n+i, [timedelta(), timedelta()])
            self.grid.add_widget(block, index=1)
            self.blocks.append(block)

        for i, block in enumerate(self.blocks):
            begin = self.min_hour + i*self.base_separation
            end = begin + self.base_separation
            block.range_hour = [begin, end]

    def add_block(self, idx: int) -> None:

        block = self.blocks[idx]
        intial_range = block.range_hour_int

        if intial_range < 2:
            return

        hour_separator = block.range_hour[0] + timedelta(hours=intial_range//2)

        added_block = DailyBlock(idx+1, [hour_separator, block.range_hour[1]])
        block.range_hour = [block.range_hour[0], hour_separator]

        self.grid.add_widget(added_block, index=len(self.grid.children)-idx-2)
        self.blocks.insert(idx+1, added_block)

        for i, block in enumerate(self.blocks):
            block.pos_id = i

        added_block.add_button.bind(
            on_release=lambda instance: self.add_block(instance.parent.parent.pos_id))
        added_block.remove_button.bind(
            on_release=lambda instance: self.remove_block(instance.parent.parent.pos_id))

    def remove_block(self, idx: int) -> None:

        if len(self.blocks) == 1:
            return

        block = self.blocks[idx]

        if idx == len(self.blocks) - 1:
            other_block = self.blocks[idx-1]
            other_block.range_hour = [
                other_block.range_hour[0], block.range_hour[1]]
        else:
            other_block = self.blocks[idx+1]
            other_block.range_hour = [
                block.range_hour[0], other_block.range_hour[1]]

        self.grid.remove_widget(block)
        self.blocks.pop(idx)

        for i, block in enumerate(self.blocks):
            block.pos_id = i

    def clear_blocks(self) -> None:
        for block in self.blocks:
            block.clean()

    def change_day(self, next: bool) -> None:
        self.current_date = self.current_date + timedelta(days=int(next)*2-1)
        self.date_label = str(self.current_date)
        self.clear_blocks()

    def update_separation(self, value: int) -> None:

        self.base_separation = timedelta(hours=value)

        from_n = self.num_blocks
        to_n = int((self.max_hour - self.min_hour) / self.base_separation)

        if from_n == to_n:
            return

        self.num_blocks = to_n
        if to_n - from_n > 0:
            self.add_blocks(from_n, to_n)
            return

        self.reduce_blocks(from_n, to_n)

    def on_selected(self, value: int, active: bool) -> None:
        if not active:
            return

        self.update_separation(value)

    def load_separation_options(self) -> None:

        total_range_hour = int(
            (self.max_hour - self.min_hour).total_seconds() // 3600)
        divisors = get_divisors(total_range_hour)

        for div in divisors:

            radioButton = RadioButton(
                str(div), "separation_options", div, on_selected=self.on_selected)
            self.separation_options.add_widget(radioButton)

            if (div == int(self.base_separation.total_seconds() // 3600)):
                radioButton.checkbox.active = True

    def save(self) -> None:
        for block in self.blocks:
            block.save_text()
