from kivy.app import App
from kivy.lang import Builder

kv = Builder.load_file("kvFiles/Schematize.kv")


class SchematizeApp(App):
    def build(self):
        return kv


if __name__ == '__main__':
    SchematizeApp().run()
