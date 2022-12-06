from datetime import date

import modules.Utilities.saveManager as saveManager
from modules.Main.abstractScheme import SchemeScreen
from modules.Daily.dailyManager import DailyManager 
from modules.Main.mainWindow import MainWindow  

from kivy.uix.screenmanager import ScreenManager

def create_scheme_from_file(scheme_type: type, identifier_key: str) -> SchemeScreen:

        if not issubclass(scheme_type, SchemeScreen):
            raise ValueError(f"Invalid scheme type: {scheme_type.__name__}")

        data = saveManager.load_scheme_data_from_file(scheme_type, identifier_key)
         
        return scheme_type.create_from_data(data, identifier_key)

class WindowManager(ScreenManager):
    
    def __init__(self, **kwargs) -> None:
        super(WindowManager, self).__init__(**kwargs)

        main_window = MainWindow()
        self.add_widget(main_window)

        daily_manager = create_scheme_from_file(DailyManager, str(date.today()))
        daily_manager.name = 'Daily'
        self.add_widget(daily_manager)



    
