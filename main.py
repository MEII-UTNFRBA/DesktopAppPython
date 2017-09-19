from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.popup import Popup
import visa
from puerto_serie import serial_ports
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector

rm = visa.ResourceManager()
vna_elegido = []
puerto_arduino=[]
inst=[]


class Main(FloatLayout):
#    def __init__(self, name):
#        self.name = name

    punto = ObjectProperty(None)

    def update(self):
        self.punto.move()

    def up(self):
        self.punto.posicion_x =0
        self.punto.posicion_y = 5
        self.update()

    def down(self):
        self.punto.posicion_x =0
        self.punto.posicion_y = -5
        self.update()

    def left(self):
        self.punto.posicion_x =-5
        self.punto.posicion_y = 0
        self.update()

    def right(self):
        self.punto.posicion_x =5
        self.punto.posicion_y = 0
        self.update()


class VNAConnectPopup(Popup):

    global rm, vna_elegido, inst

    def __init__(self, *args):
        super(VNAConnectPopup, self).__init__(*args)
        a=ObjectProperty()
        a = rm.list_resources()
        if len(a)>0:
            box = BoxLayout(orientation='vertical')
            for i in [len(a)]:
                box.add_widget(Button(
                    text=str(a[i-1]),
                    on_press = lambda *args: VNAConnectPopup.hola(self,a[i-1])))
            self.title = 'Seleccione un equipo'
            self.content=box
            self.size_hint=(0.4, 0.4)
        else:
            box = BoxLayout(orientation='vertical')
            box.add_widget(Label(text='No hay equipo conectado'))
            self.title = 'Error'
            self.content=box
            self.size_hint=(0.4, 0.4)
        box.add_widget(Button(
            text="Cancelar",
            on_press=lambda *args: VNAConnectPopup.chau(self)))
        self.auto_dismiss=False
        self.open()

    @staticmethod
    def chau(self):
        self.dismiss()

    def hola(self,*args):
        vna_elegido = args[0]
#        inst = rm.open_resource(str(vna_elegido))      #Hay que ver como hacer para que no se rompa
        print(str(vna_elegido))
        self.dismiss()


class ArduinoConnectPopup(Popup):

    global puerto_arduino

    def __init__(self, *args):
        super(ArduinoConnectPopup, self).__init__(*args)
        a=serial_ports()
        if len(a) > 0:
            box = BoxLayout(orientation='vertical')
            for i in [len(a)]:
                box.add_widget(Button(
                    text=str(a[i - 1]),
                    on_press=lambda *args: ArduinoConnectPopup.hola(self,a[i - 1])))
            self.title = 'Seleccione un equipo'
            self.content = box
            self.size_hint = (0.4, 0.4)
        else:
            box = BoxLayout(orientation='vertical')
            box.add_widget(Label(text='Verifique la conexion'))
            self.title = 'Error'
            self.content = box
            self.size_hint = (0.4, 0.4)

        box.add_widget(Button(
            text="Cancelar",
            on_press=lambda *args: ArduinoConnectPopup.chau(self)))
        self.auto_dismiss = False
        self.open()

    @staticmethod
    def chau(self):
        self.dismiss()

    def hola(self,*args):
        puerto_arduino = args[0]
        print(puerto_arduino)


class PuntoEnGrafico(Widget):

    posicion_x = NumericProperty(0)
    posicion_y = NumericProperty(0)
    posicion = ReferenceListProperty(posicion_x, posicion_y)

    def move(self):
        self.pos = Vector(self.posicion) + self.pos


class MainApp(App):
    def build(self):
        return Main()


if __name__ == '__main__':
    MainApp().run()
