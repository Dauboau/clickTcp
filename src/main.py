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

from multiplayer import ClientSocket, HostSocket # Importa classes personalizadas para lidar com a comunicação multiplayer

#Config.set('graphics', 'fullscreen', 1)

class PlayerLabel(Label):
    height_hint = NumericProperty(0.5) # Define uma propriedade numérica para a altura_hint do label
    pos_x = NumericProperty(0) # Define uma propriedade numérica para a posição X
    pos_y = NumericProperty(0) # Define uma propriedade numérica para a posição Y

    def __init__(self, **kwargs):
        super(PlayerLabel, self).__init__(**kwargs)
        self.size_hint = (1, self.height_hint) # Configura o tamanho_hint do label com base na altura_hint

    def set_pos(self, pos_x, pos_y):
        self.pos_x = pos_x # Define a posição X do label
        self.pos_y = pos_y # Define a posição Y do label

class PlayerButton(Button):
    
    num_clicks = NumericProperty(0) # Define uma propriedade numérica para o número de cliques no botão

class StartWindow(Screen):
    def __init__(self, **kwargs):
        super(StartWindow, self).__init__(**kwargs)

    def on_enter(self):
        print("StartWindow está na tela!") # Imprime uma mensagem ao entrar na tela de início

    def host(self):
        #print("host")
        # Função para lidar com a ação do botão "Host"
        layout = GridLayout(cols = 1, padding = 10) 
  
        portInput = TextInput(hint_text='port',input_filter = 'int',multiline=False,halign = 'center',font_size=80,background_color=(0,0,0,0))
        # Cria um campo de entrada de texto com uma dica, filtro de entrada de inteiros e outras configurações

        closeButton = Button(text = "Confirmar") # Cria um botão com o texto "Confirmar"
  
        layout.add_widget(portInput) # Adiciona o campo de entrada ao layout  
        layout.add_widget(closeButton) # Adiciona o botão ao layout        
  
        popup = Popup(title ='Host - Defina uma porta!', content = layout,size_hint=(None, None), size=(800, 400))
        # Cria uma janela pop-up com um título e o layout

        popup.open() # Abre a janela pop-up

        def confirma(obj):

            try:
                global port # Variável global para armazenar a porta
                port = int(portInput.text) # Converte o valor do campo de entrada em um inteiro
            except:
                Alert('Digite o valor de uma porta! Dica: 54545') # Mostra uma mensagem de alerta em caso de erro
                return

            if(port>0 and port<65535): # Verifica se a porta está no intervalo válido
                global role # Variável global para definir a função (host ou cliente)
                role = "host" # Define a função como "host"
                popup.dismiss() # Fecha a janela pop-up
                self.manager.current = 'MainWindow' # Muda para a tela principal

            else:
                Alert('O valor da porta deve ser entre 0 e 65535!') # Mostra uma mensagem de alerta em caso de porta inválida
  
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
        #self.gameOverThread = threading.Thread(target=self.check_game_over) ###########################

    def on_enter(self):
        """Função executada no momento que a tela é exibida!"""

        print("MainWindow está na tela!")

        player_button = ObjectProperty(None)
        player_label = ObjectProperty(None)
        self.player_label.set_pos(self.x, self.y)

        global last_p2_score
        last_p2_score=0
        self.player_button.num_clicks=0
        self.player_label.height_hint=0.5
        self.player_label.size_hint=(1,0.5)
        self.game_is_over = False

        global stop_threads
        stop_threads = False

        self.waitingAlert = Alert("Aguardando inimigo. Prepare-se!",dismissable=False)

        #self.check_for_game_over.start()#####################
        Thread(target=self.check_game_over).start()

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


    def check_game_over(self):
        """Verifica se o jogo acabou"""

        while True:

            global stop_threads
            if stop_threads:
                break

            with self.mutex:
                if self.player_label.height_hint <= 0:
                    Clock.schedule_once(self.endLose)
                    stop_threads = True
                elif self.player_label.height_hint >= 1:
                    Clock.schedule_once(self.endWin)
                    stop_threads = True
                time.sleep(0.1)

    def change_screen(self, *args):
        self.manager.current = 'EndWinWindow'

    def errorCritical(self,data):

        global stop_threads
        stop_threads = True

        try:
            Thread(target=self.enemy_data).join()
            print('thread 1 killed')
        except:
            pass

        try:
            Thread(target=self.user_data).join()
            print('thread 2 killed')
        except:
            pass

        try:
            self.gameOverThread.join()
            print('thread 3 killed')
        except:
            pass

        self.waitingAlert.alert.dismiss()
        Alert("Verifique o código e tente novamente!")
        self.manager.current = 'StartWindow'

    def endWin(self,data):
        self.manager.current = 'EndWinWindow'
        print("EndWinWindow está na tela!")

    def endLose(self,data):
        self.manager.current = 'EndLoseWindow'
        print("EndLoseWindow está na tela!")

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
        while True:

            global stop_threads
            if stop_threads:
                break
          
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
                print("Impossível se conectar!")
                Clock.schedule_once(self.errorCritical)
                return

        while True:

            global stop_threads
            if stop_threads:
                break

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
