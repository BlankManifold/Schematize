from __future__ import annotations
from datetime import date, timedelta
from typing import Iterator, Optional
import itertools

from modules.Daily.dailyBlock import DailyBlock
from modules.Utilities.radioButton import RadioButton
from modules.Utilities.saveManager import save_scheme_data
from modules.Main.abstractScheme import SchemeScreen
from modules.Utilities.saveManager import load_scheme_data_from_file

from kivy.properties import ObjectProperty, StringProperty
from kivy.lang import Builder


kv = Builder.load_file("kvFiles/Daily.kv")


def get_divisors(n: int) -> Iterator[int]:
    yield 1
    for i in range(2, n//2+1):
        if (n % i == 0):
            yield i
    yield n


class DailyManager(SchemeScreen):

    grid = ObjectProperty(None)
    date_label = StringProperty(None)
    separation_options = ObjectProperty(None)

    def __init__(self, daily_date: date,  min_hour: int = 6, max_hour: int = 22, base_separation: int = 1, separations_list: Optional[list[int]] = None, activities: Optional[list[str]] = None, **kwargs) -> None:

        self._init(daily_date, min_hour, max_hour,
                  base_separation, separations_list, activities)
        super().__init__(**kwargs)

        self._init_blocks()

    def _init(self,  daily_date: date, min_hour: int = 6, max_hour: int = 22, base_separation: int = 1, separations_list: Optional[list[int]] = None, activities: Optional[list[str]] = None):

        self.saved = False
        self.loaded = True

        self.current_date = daily_date
        self.date_label = str(self.current_date)
        self.min_hour = timedelta(hours=min_hour)
        self.max_hour = timedelta(hours=max_hour)
        self.base_separation = timedelta(hours=base_separation)

        if separations_list is not None:
            num_blocks = len(separations_list)
            self.separations = separations_list
        else:
            num_blocks = int((self.max_hour - self.min_hour) /
                             self.base_separation)
            self.separations = list(
                itertools.repeat(base_separation, num_blocks))

        if activities is not None:
            self.activities = activities
        else:
            self.activities = list(itertools.repeat("", num_blocks))

    def _init_blocks(self):
        
        self.blocks = list[DailyBlock]()
        self._create_blocks()
        self._bind_blocks()
        self._load_separation_options()
        self.init_dict_data()

    @property
    def identifier_key(self) -> str:
        return self.date_label

    @classmethod
    def default_data(cls) -> dict:
        dict_data = dict()
        dict_data["base_separation"] = 1
        dict_data["min_hour"] = 6
        dict_data["max_hour"] = 21

        num_blocks = (
            dict_data["max_hour"] - dict_data["min_hour"]) // dict_data["base_separation"]
        dict_data["activities"] = list(itertools.repeat("", num_blocks))
        dict_data["separations"] = list(itertools.repeat(
            dict_data["base_separation"], num_blocks))

        return dict_data

    def go_back(self) -> None:
        self.manager.transition.direction = "right"
        self.manager.current = "Main"

    def _create_blocks(self) -> None:

        num_blocks = len(self.separations)
        end = self.min_hour

        for i in range(num_blocks):
            begin = end
            end = end + timedelta(hours=self.separations[i])

            block = DailyBlock(i, [begin, end], self.activities[i])
            self.blocks.append(block)

    def _bind_blocks(self) -> None:
        for block in self.blocks:
            self.grid.add_widget(block, index=1)

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
        
        for block in self.blocks:
            self.grid.remove_widget(block)
        self.separation_options.clear_widgets()

        self.current_date = self.current_date + timedelta(days=int(next)*2-1)
        self.date_label = str(self.current_date)

        self.init_from_file(self.date_label)

        

    def update_separation(self, value: int) -> None:

        self.base_separation = timedelta(hours=value)

        from_n = len(self.blocks)
        to_n = int((self.max_hour - self.min_hour) / self.base_separation)

        if from_n == to_n:
            return

        # self.num_blocks = to_n
        if to_n - from_n > 0:
            self.add_blocks(from_n, to_n)
            return

        self.reduce_blocks(from_n, to_n)

    def on_selected(self, value: int, active: bool) -> None:
        if not active:
            return

        self.update_separation(value)

    def _load_separation_options(self) -> None:

        total_range_hour = int(
            (self.max_hour - self.min_hour).total_seconds() // 3600)
        divisors = get_divisors(total_range_hour)

        for div in divisors:
            radioButton = RadioButton(
                str(div), "separation_options", div, on_selected=self.on_selected)
            self.separation_options.add_widget(radioButton)

            if (div == int(self.base_separation.total_seconds() // 3600)):
                radioButton.checkbox.active = True

    def save_data(self) -> None:
        for block in self.blocks:
            block.save_text()
        self.init_dict_data()
        save_scheme_data(self)

    def init_from_file(self, indetifier_key: str) -> None:
        
        data = load_scheme_data_from_file(type(self), indetifier_key)
        min_hour = data["min_hour"]
        max_hour = data["max_hour"]

        base_separation = data["base_separation"]
        separations = data["separations"]
        activities = data["activities"]

        self._init(self.current_date, min_hour, max_hour,
                  base_separation, separations, activities)
        self._init_blocks()

    def init_dict_data(self) -> None:
        self.dict_data["base_separation"] = int(
            self.base_separation.total_seconds() // 3600)
        self.dict_data["min_hour"] = int(self.min_hour.total_seconds() // 3600)
        self.dict_data["max_hour"] = int(self.max_hour.total_seconds() // 3600)

        self.dict_data["activities"] = list[str]()
        for block in self.blocks:
            self.dict_data["activities"].append(block.activities)

        self.dict_data["separations"] = list[int]()
        for block in self.blocks:
            self.dict_data["separations"].append(block.range_hour_int)

    @classmethod
    def create_from_data(cls, data: dict, data_label: str) -> DailyManager:

        min_hour = data["min_hour"]
        max_hour = data["max_hour"]

        base_separation = data["base_separation"]
        separations = data["separations"]
        activities = data["activities"]

        dailyManager = cls(date.today(), min_hour, max_hour,
                           base_separation, separations, activities)

        return dailyManager
