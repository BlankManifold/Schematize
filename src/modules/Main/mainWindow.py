from kivy.uix.screenmanager import Screen

class MainWindow(Screen):

    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        
    def go_to(self, name:str) -> None:
        self.manager.transition.direction = "left"
        self.manager.current = name