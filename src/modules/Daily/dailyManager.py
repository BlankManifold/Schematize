from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

from modules.Daily.dailyBlock import DailyBlock
kv = Builder.load_file("kvFiles/Daily.kv")

class DailyManager(Screen):
    pass
