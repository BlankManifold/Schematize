from kivy.uix.screenmanager import Screen

class MainWindow(Screen):
    
    def go_to(self, name:str) -> None:
        self.manager.transition.direction = "left"
        self.manager.current = name