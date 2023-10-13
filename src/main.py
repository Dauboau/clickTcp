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
  
        closeButton.bind(on_press = confirma) # Associa a função confirma ao evento de pressionar o botão


    def client(self):
        #print("client")
        # Função para lidar com a ação do botão "Client"
        
        layout = GridLayout(cols = 1, padding = 10) # Cria um layout de grade com uma coluna e margens  
  
        portInput = TextInput(hint_text='código',input_filter = 'int',multiline=False,halign = 'center',font_size=80,background_color=(0,0,0,0))
        # Cria um campo de entrada de texto com uma dica, filtro de entrada de inteiros e outras configurações
        closeButton = Button(text = "Confirmar") # Cria um botão com o texto "Confirmar"
  
        layout.add_widget(portInput) # Adiciona o campo de entrada ao layout  
        layout.add_widget(closeButton) # Adiciona o botão ao layout        
  
        popup = Popup(title ='Digite o código do Host!', content = layout,size_hint=(None, None), size=(800, 400))
        # Cria uma janela pop-up com um título e o layout

        popup.open() # Abre a janela pop-up

        def confirma(obj):

            try:
                global port # Variável global para armazenar a porta
                port = int(portInput.text) # Converte o valor do campo de entrada em um inteiro
            except:
                Alert('Por favor, digite o código do Host!') # Mostra uma mensagem de alerta em caso de erro
                return

            if(port>0 and port<65535): # Verifica se o código está no intervalo válido
                global role # Variável global para definir a função (host ou cliente)
                role = "client" # Define a função como "cliente"
                popup.dismiss() # Fecha a janela pop-up
                self.manager.current = 'MainWindow' # Muda para a tela principal

            else:
                Alert('O valor do código deve ser entre 0 e 65535!') # Mostra uma mensagem de alerta em caso de código inválido
  
        closeButton.bind(on_press = confirma) # Associa a função confirma ao evento de pressionar o botão
    
class Alert:
    # Define uma classe para criar janelas pop-up de alerta

    def __init__(self, text_alert,dismissable=True, **kwargs):
        layoutAlert = GridLayout(cols = 1, padding = 10) # Cria um layout de grade com uma coluna e margens
        closeAlertButton = Button(text = "Ok") # Cria um botão "Ok"
        layoutAlert.add_widget(closeAlertButton) # Adiciona o botão ao layout

        self.alert = Popup(title = text_alert,content=layoutAlert,auto_dismiss=dismissable,size_hint=(None, None), size=(800, 250))
        # Cria uma janela pop-up de alerta com um título, conteúdo e outras configurações
        self.alert.open() # Abre a janela pop-up

        if(dismissable):
            closeAlertButton.bind(on_press = self.alert.dismiss) # Associa o evento de pressionar o botão à função de fechar a janela

        super(Alert, self).__init__(**kwargs)

class MainWindow(Screen):

    finish_connection = False # Variável que controla o estado da conexão
    game_is_over = False # Variável que controla se o jogo terminou ou não
    mutex = threading.Lock() # Mutex para controlar o acesso concorrente a variáveis

    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        #self.gameOverThread = threading.Thread(target=self.check_game_over) ###########################

    def on_enter(self):
        """Função executada no momento que a tela é exibida!"""

        print("MainWindow está na tela!") # Imprime uma mensagem ao entrar na tela principal

        player_button = ObjectProperty(None)
        player_label = ObjectProperty(None)
        self.player_label.set_pos(self.x, self.y) # Define a posição inicial do rótulo do jogador

        global last_p2_score
        last_p2_score=0 # Inicializa a pontuação do jogador 2
        self.player_button.num_clicks=0 # Inicializa o número de cliques do jogador
        self.player_label.height_hint=0.5 # Define a altura inicial do rótulo do jogador
        self.player_label.size_hint=(1,0.5) # Define a proporção do tamanho do rótulo
        self.game_is_over = False # Inicializa a variável que controla o estado do jogo

        global stop_threads
        stop_threads = False # Inicializa a variável que controla a execução de threads

        self.waitingAlert = Alert("Aguardando inimigo. Prepare-se!",dismissable=False)
        # Cria um alerta informando que o jogador está aguardando o oponente

        #self.check_for_game_over.start()#####################
        Thread(target=self.check_game_over).start() # Inicia uma thread para verificar o término do jogo

        if(role=="client"):

            portClient = port
            portHost = port+1

            self.sockClient = ClientSocket(port=portClient) # Inicializa o socket do cliente
            self.sockHost = HostSocket(port=portHost) # Inicializa o socket do host
            Thread(target=self.enemy_data).start() # Inicia uma thread para lidar com os dados do oponente
            

        elif(role=="host"):

            portHost = port
            portClient = port+1

            self.sockClient = ClientSocket(port=portClient) # Inicializa o socket do cliente
            self.sockHost = HostSocket(port=portHost) # Inicializa o socket do host
            Thread(target=self.user_data).start() # Inicia uma thread para lidar com os dados do jogador

    def on_click(self):

        self.player_button.num_clicks += 1 # Aumenta o número de cliques do jogador

        self.player_label.height_hint += 1 * 0.08 # Aumenta a altura do rótulo do jogador
        self.player_label.size_hint = (1, self.player_label.height_hint) # Atualiza o tamanho do rótulo


    def check_game_over(self):
        """Verifica se o jogo acabou"""

        while True:

            global stop_threads
            if stop_threads:
                break

            with self.mutex:
                if self.player_label.height_hint <= 0: # Verifica se a altura do rótulo atingiu zero (fim de jogo)
                    Clock.schedule_once(self.endLose) # Agenda uma chamada à função de fim de jogo (derrota)
                    stop_threads = True # Define a variável de parada de threads como True
                elif self.player_label.height_hint >= 1: # Verifica se a altura do rótulo atingiu 1 (vitória)
                    Clock.schedule_once(self.endWin) # Agenda uma chamada à função de fim de jogo (vitória)
                    stop_threads = True # Define a variável de parada de threads como True
                time.sleep(0.1) # Espera por um curto período de tempo

    def change_screen(self, *args):
        self.manager.current = 'EndWinWindow' # Muda para a tela de vitória

    def errorCritical(self,data):

        global stop_threads
        stop_threads = True # Define a variável de parada de threads como True

        try:
            Thread(target=self.enemy_data).join() # Tenta esperar pela thread que lida com os dados do oponente
            print('thread 1 killed') # Imprime uma mensagem de depuração
        except:
            pass

        try:
            Thread(target=self.user_data).join() # Tenta esperar pela thread que lida com os dados do jogador
            print('thread 2 killed') # Imprime uma mensagem de depuração
        except:
            pass

        try:
            self.gameOverThread.join() # Tenta esperar pela thread de verificação do término do jogo
            print('thread 3 killed') # Imprime uma mensagem de depuração
        except:
            pass

        self.waitingAlert.alert.dismiss() # Fecha o alerta de aguardo
        Alert("Verifique o código e tente novamente!") # Exibe um alerta com instruções para verificar o código
        self.manager.current = 'StartWindow' # Retorna para a tela de início

    def endWin(self,data):
        self.manager.current = 'EndWinWindow' # Muda para a tela de vitória
        print("EndWinWindow está na tela!") # Imprime uma mensagem de depuração

    def endLose(self,data):
        self.manager.current = 'EndLoseWindow' # Muda para a tela de derrota
        print("EndLoseWindow está na tela!") # Imprime uma mensagem de depuração

    def enemyFound(self,data):
        self.waitingAlert.alert.dismiss() # Fecha o alerta de aguardo

    def enemy_data(self):

        try:
            self.sockClient.connect() # Tenta estabelecer a conexão com o oponente
        except:
            print("Impossível se conectar!") # Imprime uma mensagem de erro
            Clock.schedule_once(self.errorCritical) # Agenda uma chamada à função de erro crítico
            return

        if(role=="client"):
            try:
                Thread(target=self.user_data).start() # Inicia uma thread para lidar com os dados do jogador
                Clock.schedule_once(self.enemyFound) # Agenda uma chamada à função de detecção do oponente
            except:
                print("Impossível se conectar!") # Imprime uma mensagem de erro
                Clock.schedule_once(self.errorCritical) # Agenda uma chamada à função de erro crítico
                return
        while True:

            global stop_threads
            if stop_threads:
                break
          
            global last_p2_score
            actual_p2_score = int(self.sockClient.get_data()) # Obtém os dados do oponente
            
            if(actual_p2_score > last_p2_score):
                self.player_label.height_hint -= (actual_p2_score-last_p2_score) * 0.08
                # Atualiza a altura do label com base nos dados do oponente
                self.player_label.size_hint = (1, self.player_label.height_hint)
                # Atualiza o tamanho do label
                last_p2_score = actual_p2_score # Atualiza a pontuação do jogador 2
                
            #print(actual_p2_sxcore)
        
        self.sockClient.close() # Fecha a conexão com o oponente

    def user_data(self):

        self.sockHost.connect() # Estabelece a conexão com o oponente

        if(role=="host"):
            try:
                time.sleep(0.1)
                Thread(target=self.enemy_data).start() # Inicia uma thread para lidar com os dados do oponente
                Clock.schedule_once(self.enemyFound) # Agenda uma chamada à função de detecção do oponente
            except:
                print("Impossível se conectar!") # Imprime uma mensagem de erro
                Clock.schedule_once(self.errorCritical) # Agenda uma chamada à função de erro crítico
                return

        while True:

            global stop_threads
            if stop_threads:
                break

            time.sleep(0.1)
            self.sockHost.send_data(self.player_button.num_clicks) # Envia os dados do jogador para o oponente
            #print(self.player_button.num_clicks)
        
        self.sockHost.close() # Fecha a conexão com o oponente

class EndWinWindow(Screen):
    def __init__(self, **kwargs):
        super(EndWinWindow, self).__init__(**kwargs)

class EndLoseWindow(Screen):
    def __init__(self, **kwargs):
        super(EndLoseWindow, self).__init__(**kwargs)
        
class Manager(ScreenManager):
    screen_one = ObjectProperty(None)
    screen_two = ObjectProperty(None)
# Define a classe MyApp que representa o aplicativo
class MyApp(App):
    def build(self):
        self.title = 'ClickTCP'
        Builder.load_file("style/screen.kv") # Carrega um arquivo de estilo KV
        return Manager(transition=NoTransition())

if __name__ == '__main__':
    MyApp().run()
