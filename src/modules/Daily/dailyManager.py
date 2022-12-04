from __future__ import annotations
from datetime import date, timedelta
from typing import Iterator, Optional
import itertools

from modules.Daily.dailyBlock import DailyBlock
from modules.Utilities.radioButton import RadioButton
from modules.Utilities.spinBox import SpinBox
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
    range_options = ObjectProperty(None)
    date_label = StringProperty(None)
    separation_options = ObjectProperty(None)

    def __init__(self, daily_date: date,  min_hour: int = 6, max_hour: int = 22, base_separation: int = 1, separations: Optional[list[int]] = None, activities: Optional[list[str]] = None, **kwargs) -> None:

        self._init(daily_date, min_hour, max_hour,
                   base_separation)
        super().__init__(**kwargs)

        if separations is None:
            n = (self.max_hour - self.min_hour) // self.base_separation
            separations = list(itertools.repeat(base_separation, n))

        n = len(separations)
        if activities is None:
            activities = list(itertools.repeat("", n))

        self._load_blocks(separations, activities)
        self._load_range_options()
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
        dict_data["max_hour"] = 22

        num_blocks = (
            dict_data["max_hour"] - dict_data["min_hour"]) // dict_data["base_separation"]
        dict_data["activities"] = list(itertools.repeat("", num_blocks))
        dict_data["separations"] = list(itertools.repeat(
            dict_data["base_separation"], num_blocks))

        return dict_data

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

    def _init(self,  daily_date: date, min_hour: int = 6, max_hour: int = 22, base_separation: int = 1):

        self.saved: bool = False
        self.loaded: bool = True

        self.current_date: date = daily_date
        self.date_label: str = str(self.current_date)
        self.min_hour: timedelta = timedelta(hours=min_hour)
        self.max_hour: timedelta = timedelta(hours=max_hour)
        self.base_separation: timedelta = timedelta(hours=base_separation)

    def _load_blocks(self, separations: list[int], activities: list[str]):
        self.blocks: list[DailyBlock] = list[DailyBlock]()
        self._create_blocks(separations, activities)
        self._bind_blocks()

    def _create_blocks(self, separations: list[int], activities: list[str]) -> None:

        num_blocks = len(separations)
        end = self.min_hour

        for i in range(num_blocks):
            begin = end
            end = end + timedelta(hours=separations[i])

            block = DailyBlock(i, [begin, end], activities[i])
            self.blocks.append(block)

    def _bind_blocks(self) -> None:
        for block in self.blocks:
            self.grid.add_widget(block, index=1)

            block.add_button.bind(on_release=lambda instance: self.on_add_block(
                instance.parent.parent.pos_id))
            block.remove_button.bind(
                on_release=lambda instance: self.on_remove_block(instance.parent.parent.pos_id))

    def _load_separation_options(self) -> None:

        total_range_hour = int(
            (self.max_hour - self.min_hour).total_seconds() // 3600)
        divisors = get_divisors(total_range_hour)

        for div in divisors:
            radioButton = RadioButton(
                str(div), "separation_options", div, on_selected=self.on_selected)
            # if (div == int(self.base_separation.total_seconds() // 3600)):
            #     radioButton.checkbox.active = True
            self.separation_options.add_widget(radioButton)

    def _load_range_options(self) -> None:
        min_hour_spinbox = SpinBox("Min", initial_value=int(
            self.min_hour.total_seconds() // 3600))
        max_hour_spinbox = SpinBox("Max", initial_value=int(
            self.max_hour.total_seconds() // 3600))

        self.range_options.add_widget(max_hour_spinbox)
        self.range_options.add_widget(min_hour_spinbox)

    def _init_range_options(self) -> None:
        self.range_options.children[0].current_value = int(
            self.min_hour.total_seconds() // 3600)
        self.range_options.children[1].current_value = int(
            self.max_hour.total_seconds() // 3600)

    def _init_dict_data(self) -> None:
        self.dict_data["base_separation"] = int(
            self.base_separation.total_seconds() // 3600)
        self.dict_data["min_hour"] = int(self.min_hour.total_seconds() // 3600)
        self.dict_data["max_hour"] = int(self.max_hour.total_seconds() // 3600)

        self.dict_data["activities"] = list[str]()
        self.dict_data["separations"] = list[int]()
        for block in self.blocks:
            self.dict_data["activities"].append(block.activities)
            self.dict_data["separations"].append(block.range_hour_int)

    def _append_block(self, front: bool = False) -> None:
        if front:
            begin = self.min_hour - self.base_separation
            end = self.min_hour
            self.min_hour = begin

            block = DailyBlock(0, [begin, end])
            self.grid.add_widget(block, index=len(self.grid.children)-1)
            self.blocks.insert(0, block)

            block.add_button.bind(on_release=lambda instance: self.on_add_block(
                instance.parent.parent.pos_id))
            block.remove_button.bind(on_release=lambda instance: self.on_remove_block(
                instance.parent.parent.pos_id))

            return

        begin = self.max_hour
        end = self.max_hour + self.base_separation
        self.max_hour = end

        block = DailyBlock(0, [begin, end])
        self.grid.add_widget(block, index=len(
            self.grid.children)-len(self.blocks)-1)
        self.blocks.append(block)

        block.add_button.bind(on_release=lambda instance: self.on_add_block(
            instance.parent.parent.pos_id))
        block.remove_button.bind(on_release=lambda instance: self.on_remove_block(
            instance.parent.parent.pos_id))

    def on_go_back(self) -> None:
        self.manager.transition.direction = "right"
        self.manager.current = "Main"

    def on_add_block(self, idx: int) -> None:

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
            on_release=lambda instance: self.on_add_block(instance.parent.parent.pos_id))
        added_block.remove_button.bind(
            on_release=lambda instance: self.on_remove_block(instance.parent.parent.pos_id))

    def on_remove_block(self, idx: int) -> None:

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

    def on_clear_blocks(self) -> None:
        for block in self.blocks:
            block.clean()

    def on_change_day(self, next: bool) -> None:

        for block in self.blocks:
            self.grid.remove_widget(block)
        self.separation_options.clear_widgets()

        self.current_date = self.current_date + timedelta(days=int(next)*2-1)
        self.date_label = str(self.current_date)

        self.init_from_file(self.date_label)

    def on_save(self) -> None:
        for block in self.blocks:
            block.save_text()
        self._init_dict_data()
        save_scheme_data(self)

    def on_change_range(self) -> None:

        new_min = self.range_options.children[0].current_value
        new_max = self.range_options.children[1].current_value

        if new_min > new_max:
            return

        new_min_hour = timedelta(hours=new_min)
        new_max_hour = timedelta(hours=new_max)

        to_be_removed = []
        changed = False

        if new_min_hour > self.min_hour:
            changed = True
            self.min_hour = new_min_hour
            for i, block in enumerate(self.blocks):
                if block.isbefore(new_min_hour):
                    to_be_removed.append(block)
                    continue
                break
        elif new_min_hour < self.min_hour:
            changed = True
            num_blocks = (self.min_hour - new_min_hour) // self.base_separation
            for _ in range(num_blocks):
                self._append_block(front=True)

            self.min_hour = new_min_hour

        if new_max_hour < self.max_hour:
            changed = True
            self.max_hour = new_max_hour
            for block in self.blocks[::-1]:
                if block.isafter(new_max_hour):
                    to_be_removed.append(block)
                    continue
                break
        elif new_max_hour > self.max_hour:
            changed = True
            num_blocks = (new_max_hour - self.max_hour) // self.base_separation
            for _ in range(num_blocks):
                self._append_block()

            self.max_hour = new_max_hour

        if changed:
            for block in to_be_removed:
                self.grid.remove_widget(block)
                self.blocks.remove(block)

            for i, block in enumerate(self.blocks):
                block.pos_id = i

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
            block.add_button.bind(on_release=lambda instance: self.on_add_block(
                instance.parent.parent.pos_id))
            block.remove_button.bind(
                on_release=lambda instance: self.on_remove_block(instance.parent.parent.pos_id))

        for i, block in enumerate(self.blocks):
            begin = self.min_hour + i*self.base_separation
            end = begin + self.base_separation
            block.range_hour = [begin, end]

    def update_separation(self, value: int) -> None:

        self.base_separation = timedelta(hours=value)

        from_n = len(self.blocks)
        to_n = int((self.max_hour - self.min_hour) / self.base_separation)

        if from_n == to_n:
            return

        if to_n - from_n > 0:
            self.add_blocks(from_n, to_n)
            return

        self.reduce_blocks(from_n, to_n)

    def on_selected(self, value: int, active: bool) -> None:
        if not active:
            return

        self.update_separation(value)

    def init_from_file(self, indetifier_key: str) -> None:

        data = load_scheme_data_from_file(type(self), indetifier_key)
        min_hour = data["min_hour"]
        max_hour = data["max_hour"]

        base_separation = data["base_separation"]
        separations = data["separations"]
        activities = data["activities"]

        self._init(self.current_date, min_hour, max_hour, base_separation)
        self._load_blocks(separations, activities)
        self._load_separation_options()

        self._init_range_options()
        self._init_dict_data()
