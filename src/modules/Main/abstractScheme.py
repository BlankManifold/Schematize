from __future__ import annotations
from abc import abstractmethod

from kivy.uix.screenmanager import Screen



class SchemeScreen(Screen):

    def __init__(self, **kwargs):
        super(SchemeScreen, self).__init__(**kwargs)
        self.dict_data = dict()

    @property
    @abstractmethod
    def identifier_key(self) -> str:
        pass
    
    @property
    def scheme_type(self) -> type:
        return type(self)
    
    @classmethod
    @abstractmethod
    def default_data(cls) -> dict:
        return dict()

    @abstractmethod
    def save_data(self) -> None:
        pass

    @abstractmethod
    def load_data(self) -> None:
        pass
    
    @classmethod
    @abstractmethod
    def create_from_data(cls, data:dict, identifier_key: str) -> SchemeScreen:
        pass
   
    @abstractmethod
    
    def init_dict_data(self) -> None:
        pass
