import threading
from time import sleep
import time
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

from multiplayer import ClientSocket, HostSocket

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
                global port
                port = int(portInput.text)
            except:
                Alert('Digite o valor de uma porta! Dica: 54545')
                return

            if(port>0 and port<65535):
                global role
                role = "host"
                popup.dismiss()
                self.manager.current = 'MainWindow'

            else:
                Alert('O valor da porta deve ser entre 0 e 65535!')
  
        closeButton.bind(on_press = confirma)


    def client(self):
        #print("client")

        layout = GridLayout(cols = 1, padding = 10) 
  
        portInput = TextInput(hint_text='código',input_filter = 'int',multiline=False,halign = 'center',font_size=80,background_color=(0,0,0,0))
        closeButton = Button(text = "Confirmar")
  
        layout.add_widget(portInput) 
        layout.add_widget(closeButton)        
  
        popup = Popup(title ='Digite o código do Host!', content = layout,size_hint=(None, None), size=(800, 400))

        popup.open()

        def confirma(obj):

            try:
                global port
                port = int(portInput.text)
            except:
                Alert('Por favor, digite o código do Host!')
                return

            if(port>0 and port<65535):
                global role
                role = "client"
                popup.dismiss()
                self.manager.current = 'MainWindow'

            else:
                Alert('O valor do código deve ser entre 0 e 65535!')
  
        closeButton.bind(on_press = confirma)
    
class Alert:

    def __init__(self, text_alert,dismissable=True, **kwargs):
        layoutAlert = GridLayout(cols = 1, padding = 10) 
        closeAlertButton = Button(text = "Ok")
        layoutAlert.add_widget(closeAlertButton) 

        self.alert = Popup(title = text_alert,content=layoutAlert,auto_dismiss=dismissable,size_hint=(None, None), size=(800, 250))
        self.alert.open()

        if(dismissable):
            closeAlertButton.bind(on_press = self.alert.dismiss)

        super(Alert, self).__init__(**kwargs)

class MainWindow(Screen):

    finish_connection = False
    game_is_over = False######################
    mutex = threading.Lock() ###########################

    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self.check_for_game_over = threading.Thread(target=self.check_game_over) ###########################
        

    def on_enter(self):
        """Função executada no momento que a tela é exibida!"""

        print("MainWindow está na tela!")

        player_button = ObjectProperty(None)
        player_label = ObjectProperty(None)
        self.player_label.set_pos(self.x, self.y)

        global last_p2_score
        last_p2_score=0

        self.waitingAlert = Alert("Aguardando inimigo. Prepare-se!",dismissable=False)

        self.check_for_game_over.start()#####################

        if(role=="client"):

            portClient = port
            portHost = port+1

            self.sockClient = ClientSocket(port=portClient)
            self.sockHost = HostSocket(port=portHost)
            Thread(target=self.enemy_data).start()

        elif(role=="host"):

            portHost = port
            portClient = port+1

            self.sockClient = ClientSocket(port=portClient)
            self.sockHost = HostSocket(port=portHost)
            Thread(target=self.user_data).start()

    def on_click(self):

        self.player_button.num_clicks += 1

        self.player_label.height_hint += 1 * 0.08
        self.player_label.size_hint = (1, self.player_label.height_hint)

        #verificar se o jogo acabou
#########################################################################
    def check_game_over(self):

        while not self.game_is_over:
            with self.mutex:
                if self.player_label.height_hint <= 0:
                    Clock.schedule_once(self.change_screen, 0)
                    self.game_is_over = True
                    self.finish_connection = True

                elif self.player_label.height_hint >= 1:
                    Clock.schedule_once(self.change_screen, 0)
                    self.game_is_over = True
                    self.finish_connection = True
                time.sleep(0.1)
#########################################################################

    def change_screen(self, *args):
        self.manager.current = 'EndWinWindow'

    def errorCritical(self,data):
        Alert("Verifique o código e tente novamente!")
        self.manager.current = 'StartWindow'

    def enemyFound(self,data):
        self.waitingAlert.alert.dismiss()

    def enemy_data(self):

        try:
            self.sockClient.connect()
        except:
            print("Impossível se conectar!")
            Clock.schedule_once(self.errorCritical)
            return

        if(role=="client"):
            try:
                Thread(target=self.user_data).start()
                Clock.schedule_once(self.enemyFound)
            except:
                print("Impossível se conectar!")
                Clock.schedule_once(self.errorCritical)
                return

        while not self.finish_connection:
          
            global last_p2_score
            actual_p2_score = int(self.sockClient.get_data())
            
            if(actual_p2_score > last_p2_score):
                self.player_label.height_hint -= (actual_p2_score-last_p2_score) * 0.08
                self.player_label.size_hint = (1, self.player_label.height_hint)
                last_p2_score = actual_p2_score
                
            #print(actual_p2_sxcore)
        
        self.sockClient.close()

    def user_data(self):

        self.sockHost.connect()

        if(role=="host"):
            try:
                time.sleep(0.1)
                Thread(target=self.enemy_data).start()
                Clock.schedule_once(self.enemyFound)
            except:
                #print("Impossível se conectar!")
                Clock.schedule_once(self.errorCritical)
                return

        while not self.finish_connection:
            time.sleep(0.1)
            self.sockHost.send_data(self.player_button.num_clicks)
            #print(self.player_button.num_clicks)
        
        self.sockHost.close()

class EndWinWindow(Screen):
    def __init__(self, **kwargs):
        super(EndWinWindow, self).__init__(**kwargs)

class EndLoseWindow(Screen):
    def __init__(self, **kwargs):
        super(EndLoseWindow, self).__init__(**kwargs)
        
class Manager(ScreenManager):
    screen_one = ObjectProperty(None)
    screen_two = ObjectProperty(None)

class MyApp(App):
    def build(self):
        self.title = 'ClickTCP'
        Builder.load_file("style/screen.kv")
        return Manager(transition=NoTransition())

if __name__ == '__main__':
    MyApp().run()