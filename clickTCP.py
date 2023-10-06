from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

Builder.load_file("buttons.kv")

class CustomButton(Button):
    def __init__(self, **kwargs):
        super(CustomButton, self).__init__(**kwargs)
        self.num_clicks = 0

    def increment_clicks(self, *args):
        self.num_clicks += 1
        print(self.num_clicks)

class MainApp(App):
    def build(self):
        root = BoxLayout(orientation="vertical")
        root.add_widget(CustomButton())
        
        return root

MainApp().run()