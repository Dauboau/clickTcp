import threading
from kivy.uix.popup import Popup 
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen,NoTransition
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
import random
from threading import Thread, main_thread
from kivy.clock import Clock
from kivy.config import Config

from multiplayer import ClientSocket

#Config.set('graphics', 'fullscreen', 1)

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

class StartWindow(Screen):
    def __init__(self, **kwargs):
        super(StartWindow, self).__init__(**kwargs)

    def host(self):
        #print("host")

        layout = GridLayout(cols = 1, padding = 10) 
  
        portInput = TextInput(hint_text='port',input_filter = 'int',multiline=False,halign = 'center',font_size=80,background_color=(0,0,0,0))
        closeButton = Button(text = "Confirmar")
  
        layout.add_widget(portInput) 
        layout.add_widget(closeButton)        
  
        popup = Popup(title ='Host - Defina uma porta!', content = layout,size_hint=(None, None), size=(800, 400))

        popup.open()

        def confirma(obj):

            try:
                port = int(portInput.text)
            except:
                self.alert('Digite o valor de uma porta! Dica: 54545')
                return

            print(portInput.text)

            if(port>0 and port<65535):
                self.manager.current = 'MainWindow'
                popup.dismiss()

            else:
                self.alert('O valor da porta deve ser entre 0 e 65535!')
  
        closeButton.bind(on_press = confirma)


    def client(self):
        print("client")

    def alert(self,text_alert):

        layoutAlert = GridLayout(cols = 1, padding = 10) 
        closeAlertButton = Button(text = "Ok")
        layoutAlert.add_widget(closeAlertButton) 

        alert = Popup(title = text_alert,content=layoutAlert,size_hint=(None, None), size=(800, 250))
        alert.open()

        closeAlertButton.bind(on_press = alert.dismiss)
    

class MainWindow(Screen):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)

        return 
    
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

class Manager(ScreenManager):
    screen_one = ObjectProperty(None)
    screen_two = ObjectProperty(None)

class MyApp(App):
    def build(self):
        #self.title = 'ClickTCP'
        Builder.load_file("screen.kv")
        return Manager(transition=NoTransition())

if __name__ == '__main__':
    MyApp().run()
