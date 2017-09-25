from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
import visa
from puerto_serie import serial_ports
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector

rm = visa.ResourceManager()
inst=[]


class Main(FloatLayout):

    vna_status = StringProperty()
    arduino_status = StringProperty()
    punto = ObjectProperty(None)

    def __init__(self):
        super(Main, self).__init__()
        self.vna_status="Desconectado"
        self.arduino_status = "Desconectado"
        self.vna_conectado = 0                  #Para saber si esta algo conectado o no
        self.arduino_conectado = 0              #Lo mismo pero para arduino

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

    def vna_popup(self):
        VNAConnectPopup(self.vna_popup_cb)

    def arduino_popup(self):
        ArduinoConnectPopup(self.arduino_popup_cb)

    def vna_popup_cb(self, vna_sel, status):
        self.vna_status = vna_sel
        self.vna_conectado = status
        print(self.vna_status)
        print(self.vna_conectado)

    def arduino_popup_cb(self, ar_sel, status):
        self.arduino_status = ar_sel
        self.arduino_conectado = status
        print(self.arduino_status)
        print(self.arduino_conectado)


class VNAConnectPopup(Popup):

    global rm, inst

    vna_elegido = StringProperty()

    def __init__(self,callback):
        super(VNAConnectPopup, self).__init__()
        self.vna_elegido = "Desconectado"               #HAY QUE SACARLO, esta solo para que no rompa Cancelar
        rm = visa.ResourceManager()
        a = ObjectProperty()
        a = rm.list_resources(query=u'USB?*')
        print(len(a))
        print(a)
        if len(a) > 0:
            box = BoxLayout(orientation='vertical')
            for i in range(0, len(a)):
                print(i)
                inst = rm.open_resource(str(a[i-1]))
                box.add_widget(Button(
                    text=str(inst.query("*IDN?")),
                    on_press = lambda *args: VNAConnectPopup.hola(self, callback, a[i-1],1)))
                inst.close()
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
            on_press=lambda *args: VNAConnectPopup.chau(self,callback)))
        self.auto_dismiss = False
        self.open()

    def chau(self,callback):
#        callback(self.vna_elegido)         #Solo para pruebas
        self.dismiss()

    def hola(self,callback,vna_sel,status):
        self.vna_elegido = vna_sel
        callback(self.vna_elegido,status)               #Hay que ver si se rompe por esto
#        inst = rm.open_resource(str(vna_elegido))      #Hay que ver como hacer para que no se rompa
        print(str(self.vna_elegido))
        inst = rm.open_resource(str(self.vna_elegido))
        print(inst.query("*IDN?"))
#        inst.write(":FREQ:CENT 803000")          #Para el DSA815 (SA)
        inst.close()
        self.dismiss()


class ArduinoConnectPopup(Popup):

    puerto_arduino = StringProperty()

    def __init__(self,callback):
        super(ArduinoConnectPopup, self).__init__()
        self.puerto_arduino = "Mongo"
        a=serial_ports()
        print(a)
        if len(a) > 0:
            box = BoxLayout(orientation='vertical')
            for i in range(0, len(a)):
                print(i)
                box.add_widget(Button(
                    text=str(a[i-1]),
                    on_press=lambda *args: ArduinoConnectPopup.hola(self, callback, a[i - 1],1)))
            self.title = 'Seleccione un equipo'
            self.content = box
            self.size_hint = (0.4, 0.4)
        else:
            box = BoxLayout(orientation='vertical')
            box.add_widget(Label(text='No hay equipo conectado'))
            self.title = 'Error'
            self.content = box
            self.size_hint = (0.4, 0.4)
        box.add_widget(Button(
            text="Cancelar",
            on_press=lambda *args: ArduinoConnectPopup.chau(self, callback)))
        self.auto_dismiss = False
        self.open()

    def chau(self,callback):
#        self.puerto_arduino = "Chongo"          #De prueba
#        callback(self.puerto_arduino)           #De prueba
        self.dismiss()

    def hola(self,callback,port_sel,status):
        self.puerto_arduino = port_sel          #Esta en caso de necesitarlo luego
        callback(self.puerto_arduino,status)
        self.dismiss()


class PuntoEnGrafico(Widget):

    # El grafico del smith utilizado tiene 240 "pasos" de diametro
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
