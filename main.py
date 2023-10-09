import threading
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
import random
from threading import Thread, main_thread
from kivy.clock import Clock

from multiplayer import ClientSocket

Builder.load_file("main_window.kv")

class PlayerLabel(Label):
    height_hint = NumericProperty(0.5)
    pos_x = NumericProperty(0)
    pos_y = NumericProperty(0)

    def __init__(self, **kwargs):
        super(PlayerLabel, self).__init__(**kwargs)
        self.size_hint = (1, self.height_hint)

    def set_pos(self, pos_x, pos_y):
        self.pos_x = pos_x
        self.pos_y = pos_y

class PlayerButton(Button):
    
    num_clicks = NumericProperty(0)

class MainWindow(FloatLayout):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        player_button = ObjectProperty(None)
        player_label = ObjectProperty(None)
        self.player_label.set_pos(self.x, self.y)

        self.sockClient = ClientSocket() # port can be an argument
        Thread(target=self.enemy_data).start()

    def on_click(self):

        self.player_button.num_clicks += 1

        self.player_label.height_hint += 1 * 0.1
        self.player_label.size_hint = (1, self.player_label.height_hint)

        #verificar se o jogo acabou

    def enemy_data(self):
        while True:
          
            p2_data = int(self.sockClient.get_data())
            
            self.player_label.height_hint -= p2_data * 0.1
            self.player_label.size_hint = (1, self.player_label.height_hint)
                
            #print(p2_data)

class MyApp(App):
    def build(self):
        return MainWindow()

if __name__ == '__main__':
    MyApp().run()
