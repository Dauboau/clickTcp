from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty

Builder.load_file("main_window.kv")

class PlayerLabel(Label):
    height_hint = NumericProperty(0.5)

    def __init__(self, **kwargs):
        super(PlayerLabel, self).__init__(**kwargs)
        self.size_hint = (1, self.height_hint)


    def resize_label(self, inc):
        self.height_hint += inc
        self.size_hint = (1, self.height_hint)


class PlayerButton(Button):
    
    num_clicks = NumericProperty(0)

class MainWindow(FloatLayout):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        player_button = ObjectProperty(None)
        player_label = ObjectProperty(None)

    def on_click(self):
        self.player_button.num_clicks = self.player_button.num_clicks + 1
        self.player_label.height_hint += 0.1
        self.player_label.size_hint = (1, self.player_label.height_hint)
        print(self.player_button.num_clicks)

class MyApp(App):
    def build(self):
        return MainWindow()

if __name__ == '__main__':
    MyApp().run()
